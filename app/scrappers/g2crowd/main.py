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
    frame_one = page.wait_for_selector("iframe").content_frame()
    time.sleep(2)
    span = frame_one.wait_for_selector("input")
    if span.is_visible():
        span.click()
        time.sleep(3)
    review_data = {}
    product_name_tree = page.wait_for_selector("div.product-head__title")
    # Execute JavaScript to get the inner text of the first <a> tag within product_name
    product_name = page.evaluate(
        "(element) => element.querySelector('a').innerText", product_name_tree
    )
    print(product_name)
    pricing_cards = page.query_selector_all("a.preview-cards__card")
    if pricing_cards.is_visible():
        for a_tag in pricing_cards:
            # Execute JavaScript to extract text content from the <a> tag
            extracted_data = page.evaluate(
                """(element) => {
    const supportText = element.querySelector(".preview-cards__text").textContent;
                const dollarUnit = element.querySelector(".money__unit").textContent;
                const dollarValue = element.querySelector(".money__value").textContent;
                const billingText = element.querySelector(
                    ".preview-cards__text--fw-regular"
                ).textContent;
                return { supportText, dollarUnit, dollarValue, billingText };
            }""",
                a_tag,
            )

            pricing = {}
            pricing["support_text"] = extracted_data["supportText"]
            pricing["dollar_unit"] = extracted_data["dollarUnit"]
            pricing["dollar_value"] = extracted_data["dollarValue"]
            pricing["billing_text"] = extracted_data["billingText"]
            review_data["pricing"] = pricing

    # Rating part
    # Locate the element by its CSS selector
    rating_element = page.query_selector("span.c-midnight-90.pl-4th")

    if rating_element:
        # Execute JavaScript to extract the complete rating information
        complete_rating = page.evaluate(
            """(element) => {
            return element.textContent.trim();
        }""",
            rating_element,
        )

        # Now, complete_rating contains the extracted complete rating (e.g., "4.3 out of 5")
        print("Complete Rating:", complete_rating)
    else:
        print("Rating element not found")
    return "NA"


def g2crowd_scrapper(url: str):
    with sync_playwright() as play:
        time.sleep(2)
        browser = play.chromium.launch(headless=False, devtools=True)
        time.sleep(3)
        context = browser.new_context()
        page = context.new_page()

        time.sleep(1)
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
