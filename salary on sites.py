import json
import requests
import os 
from terminaltables import AsciiTable 
from dotenv import load_dotenv 


PROGRAMMING_LANGUEAGES = ["JavaScript", "Java","Python", "Ruby", "PHP", "C++", "C", "C#"]

def calculate_salary(salary_from, salary_to): 
    salary = ((salary_from or 0.8 * salary_to) + (salary_to or 1.2 * salary_from)) / 2
    return salary

def fetch_hh_vacancies(language):
    url = "https://api.hh.ru/vacancies"
    moscow_location_id = 1 
    num_days = 30 
    posts_per_page = 100 
    all_vacancies = []  
    page = 0
    while True:
        payload = {
            "text": f"программист {language}",
            "area": moscow_location_id,
            "only_with_salary": True,
            "period": num_days,
            "per_page": posts_per_page,
            "page": page 
        
        }
        response = requests.get(url, params=payload) 
        response.raise_for_status() 
        vacancies = response.json() 

        page_payload = vacancies.get("items", 0) 
        all_vacancies.extend(page_payload)
    
        total_pages = vacancies.get('pages', 0) 
        if page >= total_pages - 1: 
            break 
        page += 1  
    total_vacancies = vacancies.get('found', 0)    

    return total_vacancies, all_vacancies


def predict_hh_salary(vacancies):
    average_salaries = []

    for vacancy in vacancies:
        salary_meaning = vacancy.get('salary', {})
        salary_currency = salary_meaning.get('currency')
        salary_from = salary_meaning.get('from')
        salary_to = salary_meaning.get("to")
        if salary_currency != 'RUR' or (salary_from is False and salary_to is False):
            continue
        salary = calculate_salary(salary_from, salary_to)
        average_salaries.append(salary)
    processed_count = len(average_salaries)
    if average_salaries:
        total_salary = int(sum(average_salaries) / processed_count)
        return total_salary, processed_count 
    return None, 0


def fetch_superjob_vacancies(superjob_token, language):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies_from_superjob = []
    page = 0 
    found_vacancies = 0 
    number_of_posts_per_page = 100
    while True:
        payload = {
            'town': "Москва",
            'keyword': f'программист {language}',
            'page': page,
            'count': number_of_posts_per_page
        }
        headers = {
            'X-Api-App-Id': superjob_token
        }

        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()  
        superjob_vacancies = response.json()
        vacancies = superjob_vacancies.get('objects', []) 
        has_next_page = superjob_vacancies.get('more', False)
        if not vacancies:
            break
        vacancies_from_superjob.extend(vacancies) 
        found_vacancies += len(vacancies) 
        if not has_next_page: 
            break
        page += 1
    return vacancies_from_superjob, found_vacancies


def predict_rub_salary_for_superJob(vacancies_from_superjob):
    average_salaries = []
    for vacancy in vacancies_from_superjob:
        salary_from = vacancy.get('payment_from')
        salary_to = vacancy.get("payment_to") 
        if  salary_from  or salary_to:
            salary = calculate_salary(salary_from, salary_to)
            average_salaries.append(salary) 
    processed_count = len(average_salaries)
    if average_salaries:
        total_salary = int(sum(average_salaries) / processed_count )
        return total_salary, processed_count
    return None, 0 


def create_and_print_table(file,title): 
    table = AsciiTable(file, title)
    table.justify_columns[1] = 'right' 
    table.justify_columns[2] = 'right'  
    print(table.table)

def main():
    load_dotenv()
    superjob_token = os.environ["TOKEN_SUPERJOB"] 

    headhunters_search_results = [] 
    superjob_search_results = []
 

    table_column_names = ['Язык программирования', 'Всего вакансий', 'Подходящих вакансий', 'Средняя зарплата']

    headhunters_search_results.append(table_column_names)
    superjob_search_results.append(table_column_names)
    
    for language in PROGRAMMING_LANGUEAGES:
        total_vacancies, all_vacancies = fetch_hh_vacancies(language)
        total_salary, count = predict_hh_salary(all_vacancies)   
        row_headhunters = [language, total_vacancies, count, total_salary or "-"] 
        headhunters_search_results.append(row_headhunters) 

        vacancies_from_superjob, found_vacancies = fetch_superjob_vacancies(superjob_token, language)
        total_salary, processed_count = predict_rub_salary_for_superJob(vacancies_from_superjob)
        row_superjob = [language, found_vacancies, processed_count, total_salary or"-"]
        superjob_search_results.append(row_superjob) 
 
    create_and_print_table(headhunters_search_results, "HeadHunters Москва")    
    create_and_print_table(superjob_search_results, "SuperJob Москва")


if __name__ == "__main__":
    main()


