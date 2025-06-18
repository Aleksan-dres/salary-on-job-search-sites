import json
import requests
import os 
from terminaltables import AsciiTable 
from dotenv import load_dotenv 


programming_languages = ["JavaScript", "Java",
                         "Python", "Ruby", "PHP", "C++", "C", "C#"]


def fetch_hh_vacancies(language):
    url = "https://api.hh.ru/vacancies"

    payload = {
        "text": f"программист {language}",
        "area": 1,
        "only_with_salary": True,
        "period": 30,
        "per_page": 100
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()
    vacancies = response.json()

    total_vacancies = vacancies.get('found', 0)
    total_pages = vacancies.get('pages', 0)

    all_vacancies = []
    for page in range(total_pages):
        payload['page'] = page
        page_response = requests.get(url, params=payload)
        page_response.raise_for_status()
        page_payload = page_response.json()
        all_vacancies.extend(page_payload['items'])
    

    return total_vacancies, all_vacancies


def predict_hh_salary(vacancies):
    average_salary = []
    processed_count = 0


    for vacancy in vacancies:
        salary_meaning = vacancy.get('salary', {})
        money = salary_meaning.get('currency')
        salary_from = salary_meaning.get('from')
        salary_to = salary_meaning.get("to")
        if money != 'RUR' or ((salary_from is None and salary_from == 0) and (salary_to is None and salary_to == 0)):
            continue
        elif salary_from == None:
            salary = 0.8 * salary_to
        elif salary_to == None:
            salary = 1.2 * salary_from
        else:
            salary_from and salary_to
            salary = (salary_from + salary_to) / 2
        processed_count += 1
        average_salary.append(salary)

    if average_salary:
        total_salary = int(sum(average_salary) / len(average_salary))
        return total_salary, processed_count 
    return None, 0


def search_sj_job(job_token, language):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    name_vacancy = []
    page = 0
    while True:
        payload = {
            'town': "Москва",
            'keyword': f'программист {language}',
            'page': page,
            'count': 100
        }
        headers = {
            'X-Api-App-Id': job_token
        }

        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        vacancies = response.json().get('objects', [])
        if not vacancies:
            break
        name_vacancy.extend(vacancies)
        page += 1
    return name_vacancy


def predict_rub_salary_for_superJob(name_vacancies):
    average_salary = []
    processed_count = 0
    for vacancy in name_vacancies:
        salary_from = vacancy.get('payment_from')
        salary_to = vacancy.get("payment_to")
        if (salary_from is not None and salary_from > 0) or (salary_to is not None and salary_to > 0):

            if salary_from is None:
                salary = 0.8 * salary_to
            elif salary_to is None:
                salary = 1.2 * salary_from
            else:
                salary = (salary_from + salary_to) / 2
            processed_count += 1
            average_salary.append(salary)
    if average_salary:
        total_salary = int(sum(average_salary) / len(average_salary))
        return total_salary, processed_count
    return None, 0

def main():
    load_dotenv()
    job_token = os.environ["TOKEN_JOB"] 

    hh_results = [] 
    sj_result = []

    title_hh = "HeadHunters Москва"
    title_sj = "SuperJob Москва"  

    hh_results.append(['Язык программирования', 'Всего вакансий', 'Подходящих вакансий', 'Средняя зарплата'])
    sj_result.append(['Язык программирования', 'Всего вакансий', 'Подходящих вакансий', 'Средняя зарплата'])
    
    for language in programming_languages:
        total_vacancies, all_vacancies = fetch_hh_vacancies(language)
        total_salary, count = predict_hh_salary(all_vacancies)
        row = [language, total_vacancies, count, total_salary if total_salary is not None else "-"] 
        hh_results.append(row) 

    table = AsciiTable(hh_results, title_hh)
    table.justify_columns[1] = 'right' 
    table.justify_columns[2] = 'right'  
    print(table.table)

    for language in programming_languages:
        name_vacancy = search_sj_job(job_token, language)
        total_count = len(name_vacancy)
        total_salary, processed_count = predict_rub_salary_for_superJob(
            name_vacancy)
        row = [language, total_count, processed_count, total_salary if total_salary is not None else "-"]
        sj_result.append(row) 
        
    table = AsciiTable(sj_result, title_sj)
    table.justify_columns[1] = 'right' 
    table.justify_columns[2] = 'right'  
    print(table.table)


if __name__ == "__main__":
    main()
