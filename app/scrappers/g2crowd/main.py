import os
import time
from playwright.sync_api import sync_playwright, Page
from app.scrappers.common import CsvUtility

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def get_review_data(page: Page, g2crowd_url: str):
    time.sleep(3)
    page.goto(g2crowd_url)
    time.sleep(5)
    iframe_title = "Widget containing a Cloudflare security challenge"
    frame_one = page.wait_for_selector("iframe").content_frame()
    time.sleep(2)
    span = frame_one.wait_for_selector("input")
    breakpoint()
    if span.is_visible():
        span.click()
    return "NA"


def g2crowd_scrapper(url: str):
    with sync_playwright() as play:
        time.sleep(2)
        browser = play.chromium.launch(headless=False, devtools=True)
        time.sleep(3)
        context = browser.new_context();
        page = context.new_page();
        
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        });
        time.sleep(1)
        print(play)
        review_data = get_review_data(page, url)
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
