# pylint: disable=R0914,R0915

import os
import time
from playwright.sync_api import sync_playwright, Page
from app.scrappers.common import CsvUtility

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def get_review_data(page: Page, g2crowd_url: str):
    page.goto(g2crowd_url)
    frame_one = page.wait_for_selector("iframe").content_frame()
    span = frame_one.wait_for_selector("input")
    if span.is_visible():
        span.click()
        time.sleep(2)
    review_data = {"reviews": []}

    # PRODUCT PART ###
    product_name_tree = page.wait_for_selector("div.product-head__title")
    product_name = page.evaluate(
        "(element) => element.querySelector('a').innerText", product_name_tree
    )
    review_data["product_name"] = product_name

    # PRICING PART ###
    pricing_cards = page.query_selector_all("a.preview-cards__card")
    if pricing_cards[0].is_visible():
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

    # RATING PART ###
    rating_element = page.query_selector("span.c-midnight-90.pl-4th")

    if rating_element:
        # Execute JavaScript to extract the complete rating information
        complete_rating = page.evaluate(
            """(element) => {
            return element.textContent.trim();
        }""",
            rating_element,
        )

        print("Complete Rating:", complete_rating)
        review_data["rating"] = rating_element

    # USER REVIEWS PART ###
    itemtype = "http://schema.org/Review"
    itemprop = "review"

    # Use Playwright's locator to find the element
    review_elements = page.locator(
        f'//div[@itemtype="{itemtype}" and @itemprop="{itemprop}"]'
    )
    count = review_elements.count()
    if review_elements:
        for i in range(count):
            review = {}
            review_element = review_elements.nth(i)

            # Reviewer name
            link_locator = review_element.locator(".link--header-color")

            if link_locator.count() > 0:
                # Get the content inside the <a> tag
                reviewer_name = link_locator.inner_text()

            # Reviewer role and company
            reviewer_info_locator = review_element.locator(
                ".c-midnight-80.line-height-h6.fw-regular"
            )
            reviewer_info_elements = reviewer_info_locator.all()
            if reviewer_info_elements:
                reviewer_info_element = reviewer_info_elements[0]
                reviewer_info = reviewer_info_element.inner_text().strip()
                company_start = reviewer_info.find(
                    "("
                )  # Find the start of the company information
                if company_start != -1:
                    raw_reviewer_info = reviewer_info[:company_start].strip()
                    role, company_size = raw_reviewer_info.split("\n")
                    review["role"] = role
                    review["company_size"] = company_size
                    review["employeers"] = reviewer_info[company_start:].strip()

            review["reviewer_name"] = reviewer_name
            review_data["reviews"].append(review)

    else:
        print("No review elements found")
    return review_data


def g2crowd_scrapper(url: str):
    with sync_playwright() as play:
        time.sleep(2)
        browser = play.chromium.launch(headless=False, devtools=True)
        time.sleep(3)
        context = browser.new_context()
        page = context.new_page()

        time.sleep(1)
        review_data = get_review_data(page, url)
        return review_data


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
