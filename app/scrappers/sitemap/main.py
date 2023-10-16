import os
import re
import time
import logging
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, Page
from app.scrappers.common import CsvUtility
from app.scrappers.sitemap.keywords import keywords_list


# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


"""def has_sitemap_xml(url):
    # Construct the URL for the sitemap.xml file.
    sitemap_url = f"{url}sitemap.xml"
    # Send an HTTP GET request to the sitemap URL.
    response = requests.get(sitemap_url)

    # Check if the response status code is 200, indicating the sitemap.xml file exists.
    if response.status_code == 200:
        return True
    else:
        return False
"""

def extract_urls_with_keyword(text):
    urls = []
    breakpoint()
    for keyword in keywords_list:
        # Define a regular expression pattern to match HTTP URLs containing the keyword.
        pattern = rf'https?://[^\s]*{keyword}[^\s]*'
        matched_urls = re.findall(pattern, text)
        urls.append(matched_urls)
    return urls


def get_sitemap_text(url):
    try:
        sitemap_url = f"{url}sitemap.xml"
        response = requests.get(sitemap_url)
        breakpoint()
        # Check if the request was successful (status code 200) and that the content is text-based.
        if response.status_code == 200 and 'text' in response.headers.get('Content-Type'):
            return response.text
        else:
            print(f"Failed to retrieve content from {url}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching content from {url}: {str(e)}")


def sitemap_scrapper(url: str):
    with sync_playwright() as play:
        logging.info("Starting sitemap scrapper for %s", url)
        try:
            browser = play.chromium.launch(headless=False)
            page = browser.new_page()
            breakpoint()
            text = get_sitemap_text(url)
            urls = extract_urls_with_keyword(text)
            print(urls)
            browser.close()
            return True
        except Exception as exception:
            logging.error("An error occurred: %s", exception)
            return None


def sitemap_orchestrator(relative_path: str):
    """
    This function will call the orchestrator that checks for case studies
    """
    logging.info("Starting sitemap_orchestrator")
    start_time = time.time()

    csv_input = os.path.join(script_dir, relative_path)
    csv_utility = CsvUtility()
    urls = csv_utility.read_csv_file(csv_input)

    for url in urls:
        result = sitemap_scrapper(url)

    # Output CSV with companies url's
    relative_path = "companies_output.csv"
    csv_output = os.path.join(script_dir, relative_path)
    csv_utility.list_to_csv(urls, csv_output)

    # Calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info("TIME TO EXECUTE SITEMAP: %s", elapsed_time)
    return True