import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.exceptions import CustomException, ValidationException
import re


os.chdir(os.path.dirname(os.path.abspath(__file__)))

def read_csv_file(file_path):
    print(f"Reading csv file {file_path}")
    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            result = []
            for row in csv_reader:
                result.append(row[0])
            return result
    except FileNotFoundError as err:
        print(f"File not found: {file_path}")
        message = err.args[1]
        raise ValidationException(validation_message=message) from err
    except Exception as exception:
        print(f"An error occurred: {exception}")
        raise CustomException("An error occurred", 500) from exception


def list_to_csv(_list, csv_file_path):
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write each URL to a new row in the CSV file
        for url in _list:
            csv_writer.writerow([url])


def google_search(query):
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://google.com')
        breakpoint()
        search_bar = page.query_selector('textarea')
        if search_bar.is_visible():
            search_bar.fill(query)
        employee_element = page.query_selector('a.face-pile__cta')
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', employee_element.inner_text())
        return numbers[0]



def get_employee_count(linkedin_url):
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(linkedin_url)
        time.sleep(3)
        breakpoint()
        dismiss_button = page.query_selector('button.modal__dismiss')
        if dismiss_button.is_visible():
            dismiss_button.click()
        employee_element = page.query_selector('a.face-pile__cta')
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', employee_element.inner_text())
        return numbers[0]


def company_thread(csv_input, country):
    print("Running company csv thread")
    companies_list = read_csv_file(csv_input)
    linkedin_urls = []
    for company in companies_list:
        query = f"{company}+{country}"
        company_linkedin = google_search(query)
        linkedin_urls.append(company_linkedin)

    csv_file_path = "companies_output.csv"
    list_to_csv(linkedin_urls, csv_file_path)

    print(f"URLs have been saved to {csv_file_path}")

    employee_count_list = []
    for linkedin_url in linkedin_urls:
        employee_count = get_employee_count(linkedin_url)
        employee_count_list.append(
            {"url": linkedin_url, "employee_count": employee_count}
        )
    print(employee_count_list)
