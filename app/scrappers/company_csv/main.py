import os
import re
import csv
import time
from playwright.sync_api import sync_playwright, Page

from app.exceptions import CustomException, ValidationException


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


def google_first_link(page: Page, query: str):
    page.goto("https://google.com")
    search_bar = page.query_selector("textarea")
    if search_bar.is_visible():
        search_bar.fill(query)
        # Simulate pressing the "Enter" key
        page.keyboard.press("Enter")
        time.sleep(1)
        results_list = page.query_selector_all("div.MjjYud")
        # Assuming div_element is the div element you want to work with
        a_tag_handle = results_list[0].query_selector("a:first-child")

        # Get the href attribute of the first A tag
        href = a_tag_handle.get_attribute("href")
        return href
    return "NA"


def get_employee_count(page: Page, linkedin_url: str):
    page.goto(linkedin_url)
    time.sleep(1)
    dismiss_button = page.query_selector("button.modal__dismiss")
    if dismiss_button.is_visible():
        dismiss_button.click()
    employee_element = page.query_selector("a.face-pile__cta")
    numbers = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", employee_element.inner_text())
    return numbers[0]


def linkedin_scrapper(company: str, country: str):
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()

        query = f"linkedin+{company}+{country}"
        company_page = google_first_link(page, query)
        employee_count = get_employee_count(page, company_page)
        browser.close()
        return {"url": company_page, "employee_count": employee_count}


def company_thread(csv_input, country):
    print("Running company csv thread")
    companies_list = read_csv_file(csv_input)
    final_result = []
    urls = []
    for company in companies_list:
        scrapper_data = linkedin_scrapper(company, country)
        urls.append(scrapper_data["url"])
        final_result.append(scrapper_data)

    # Output CSV with companies url's
    csv_file_path = "companies_output.csv"
    list_to_csv(urls, csv_file_path)

    print(f"URLs have been saved to {csv_file_path}")

    print(f"Final result {final_result}")
