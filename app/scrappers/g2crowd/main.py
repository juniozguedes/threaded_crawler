import os
from playwright.sync_api import sync_playwright
import cfscrape
from app.scrappers.common import CsvUtility

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def get_review_data(g2crowd_url: str):
    scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
    # Or: scraper = cfscrape.CloudflareScraper()  # CloudflareScraper inherits from requests.Session
    print(scraper.get(g2crowd_url).content)  # => "<!DOCTYPE html><html><head>..."
    return True


def g2crowd_scrapper(url: str):
    with sync_playwright() as play:
        print(play)
        review_data = get_review_data(url)
        print(review_data)
        return True


def crowd2url_thread():
    """
    This thread will call the orchestrator that scraps g2crowd
    """
    print("Running g2crowd thread")

    relative_path = "g2crowd_input.csv"
    csv_input = os.path.join(script_dir, relative_path)
    csv_utility = CsvUtility()
    g2crowd_url_list = csv_utility.read_csv_file(csv_input)
    final_result = []
    for url in g2crowd_url_list:
        scrapper_data = g2crowd_scrapper(url)
        final_result.append(scrapper_data)

    # Output json with data review

    print("Json have been saved")

    print(f"Final result {final_result}")
