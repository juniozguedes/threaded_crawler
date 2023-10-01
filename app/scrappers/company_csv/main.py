import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.exceptions import CustomException, ValidationException

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def google_search(query):
    url = f"https://www.google.com/search?q={query}+linkedin"
    pattern = f"company/{query}"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all <a> (anchor) tags in the parsed HTML
        links = soup.find_all("a")

        # Iterate through the links and check for the pattern
        for link in links:
            href = link.get("href")
            if href and pattern in href:
                # Find the index of "https://"
                start_index = href.find("https://")

                # Find the index of the query string
                end_index = href.find(query) + len(query)

                # Extract the desired substring
                desired_link = href[start_index:end_index]
        return desired_link
    print("Failed to retrieve search results.")
    return False


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


def get_employee_count(linkedin_url):
    with sync_playwright() as play:
        browser = play.chromium.launch()
        page = browser.new_page()
        page.goto(linkedin_url)
        span = page.locator('xpath=//*[@id="ember29"]/span')
        print(span)
        time.sleep(2)
        return True


def company_thread(csv_input):
    print("Running company csv thread")
    companies_list = read_csv_file(csv_input)
    linkedin_urls = []
    for company in companies_list:
        company_linkedin = google_search(company)
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
