import os
import re
import time
import logging
from playwright.sync_api import sync_playwright, Page
from app.scrappers.common import CsvUtility

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def google_first_link(page: Page, query: str):
    logging.info("Getting google first link for query: %s", query)
    try:
        page.goto("https://google.com")
        search_bar = page.query_selector("textarea")
        if search_bar.is_visible():
            search_bar.fill(query)
            # Simulate pressing the "Enter" key
            page.keyboard.press("Enter")
            time.sleep(1)
            results_list = page.query_selector_all("div.MjjYud")
            a_tag_handle = results_list[0].query_selector("a:first-child")
            # Get the href attribute of the first A tag
            href = a_tag_handle.get_attribute("href")
            return href
        logging.warning("Search bar was not found on google_first_link")
        return None
    except Exception as exception:
        logging.error("An error occurred: %s", exception)
        return None


def get_employee_count(page: Page, linkedin_url: str):
    logging.info("Getting employee count for %s", linkedin_url)
    try:
        page.goto(linkedin_url)
        time.sleep(1)
        dismiss_button = page.query_selector("button.modal__dismiss")
        # Dismiss linkedin ad
        if dismiss_button.is_visible():
            dismiss_button.click()
        employee_element = page.locator("a.face-pile__cta")
        numbers = re.findall(
            r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", employee_element.inner_text()
        )
        return numbers[0]
    except Exception as exception:
        logging.error("An error occurred: %s", exception)
        return None


def linkedin_scrapper(company: str, country: str):
    with sync_playwright() as play:
        logging.info("Starting linkedin scrapper for %s in %s", company, country)
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()

        query = f"linkedin+{company}+{country}"
        company_page = google_first_link(page, query)
        employee_count = get_employee_count(page, company_page)
        browser.close()
        return {"url": company_page, "employee_count": employee_count}


def company_thread(country: str, relative_path: str):
    """
    This thread will call the orchestrator that scraps linkedin
    Outputs: companies_output.csv with all company url's
    return: final_result with company page and employee count
    """
    logging.info("Starting company_thread")
    start_time = time.time()

    relative_path = "companies_input.csv"
    csv_input = os.path.join(script_dir, relative_path)

    csv_utility = CsvUtility()
    companies_list = csv_utility.read_csv_file(csv_input)
    final_result = []
    urls = []
    for company in companies_list:
        scrapper_data = linkedin_scrapper(company, country)
        urls.append(scrapper_data["url"])
        final_result.append(scrapper_data)

    # Output CSV with companies url's
    relative_path = "companies_output.csv"
    csv_output = os.path.join(script_dir, relative_path)

    csv_utility.list_to_csv(urls, csv_output)

    logging.info("URLs have been saved to %s", csv_output)
    logging.info("Final result %s", final_result)

    # Calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info("Time to execute company_thread: %s", elapsed_time)
    return elapsed_time
