# pylint: disable=R0914,R0915

import os
import time
import json
import logging
from playwright.sync_api import sync_playwright, Page
from app.scrappers.common import CsvUtility, PlaywrightUtility

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def bypass_cloudfare(page: Page):
    logging.info("Bypassing cloudfare")
    frame_one = page.wait_for_selector("iframe").content_frame()
    span = frame_one.wait_for_selector("input")
    if span.is_visible():
        span.click()
        time.sleep(2)
        return True
    return None


def get_review_pricing(page: Page):
    logging.info("Getting g2crowd review pricing")
    pw_utility = PlaywrightUtility()
    pricing_elements = page.locator('//a[@class="c-midnight-80 preview-cards__card"]')
    count = pricing_elements.count()
    if pricing_elements:
        pricing = []
        for i in range(count):
            current_card = {}
            pricing_element = pricing_elements.nth(i)

            support_text = pw_utility.locate_text(
                pricing_element, "span.preview-cards__text"
            )
            dollar_unit = pw_utility.locate_text(pricing_element, "span.money__unit")
            dollar_value = pw_utility.locate_text(pricing_element, "span.money__value")
            billing_text = pw_utility.locate_text(
                pricing_element, ".preview-cards__text--fw-regular"
            )

            current_card["support_text"] = support_text
            current_card["dollar_unit"] = dollar_unit
            current_card["dollar_value"] = dollar_value
            current_card["billing_text"] = billing_text
            pricing.append(current_card)
        return pricing
    return None


def get_review_rating(page: Page):
    logging.info("Getting g2crowd review rating")
    rating_element = page.query_selector("span.c-midnight-90.pl-4th")

    if rating_element:
        # Execute JavaScript to extract the complete rating information
        complete_rating = page.evaluate(
            """(element) => {
            return element.textContent.trim();
        }""",
            rating_element,
        )
        return complete_rating
    return None


def get_users_reviews(page: Page):
    logging.info("Getting g2crowd first page user review")
    itemtype = "http://schema.org/Review"
    itemprop = "review"

    review_elements = page.locator(
        f'//div[@itemtype="{itemtype}" and @itemprop="{itemprop}"]'
    )
    count = review_elements.count()
    if review_elements:
        user_reviews = []
        for i in range(count):
            review = {}
            review_element = review_elements.nth(i)

            # Reviewer name
            link_locator = review_element.locator(".link--header-color")

            if link_locator.count() > 0:
                # Get the content inside the <a> tag
                reviewer_name = link_locator.inner_text()
            else:
                reviewer_name = None

            # Reviewer role and company
            reviewer_info_locator = review_element.locator(
                ".c-midnight-80.line-height-h6.fw-regular"
            )
            reviewer_info_elements = reviewer_info_locator.all()
            if reviewer_info_elements:
                reviewer_info_element = reviewer_info_elements[0]
                reviewer_info = reviewer_info_element.inner_text().strip()

                # Split the string by the newline character '\n'
                info_parts = reviewer_info.split("\n")

                # Check if we have at least two parts
                if len(info_parts) >= 2:
                    role = info_parts[0]  # 'Co-Founder & CEO'
                    company_size = info_parts[1]  # 'Mid-Market(51-1000 emp.)'
                else:
                    role = reviewer_info  # If there's only one part, consider it as the role
                    company_size = (
                        None  # Set company_size to None or another default value
                    )
            # User reviews
            user_review_header = review_element.locator("h3.m-0").inner_text()
            user_review_element = review_element.locator('div[itemprop="reviewBody"]')
            like_heading = user_review_element.locator("text=What do you like best")
            dislike_heading = user_review_element.locator(
                "text=What do you dislike about"
            )

            like_texts = []
            dislike_texts = []
            # Extract the text content from the headings' siblings (the paragraphs)
            if like_heading and dislike_heading:
                like_paragraphs = like_heading.locator(
                    "xpath=following-sibling::div[1]/p"
                ).all()
                dislike_paragraphs = dislike_heading.locator(
                    "xpath=following-sibling::div[1]/p"
                ).all()

                like_list = [paragraph.inner_text() for paragraph in like_paragraphs]
                dislike_list = [
                    paragraph.inner_text() for paragraph in dislike_paragraphs
                ]

                for i, text in enumerate(like_list):
                    if text.strip():
                        like_texts.append(text)

                for i, text in enumerate(dislike_list):
                    if text.strip():
                        dislike_texts.append(text)

            review["reviewer_name"] = reviewer_name
            review["role"] = role
            review["company_size"] = company_size
            review["user_review"] = {
                "header": user_review_header,
                "like_texts": like_texts,
                "dislike_texts": dislike_texts,
            }
            user_reviews.append(review)
        return user_reviews
    return None


def get_review_data(page: Page, g2crowd_url: str):
    """
    This crawls the g2crowd dom in separated functions by review part
    return: review_data with the json output
    """
    page.goto(g2crowd_url)
    bypass_cloudfare(page)

    review_data = {}

    # PRODUCT PART ###
    product_name_tree = page.wait_for_selector("div.product-head__title")
    product_name = page.evaluate(
        "(element) => element.querySelector('a').innerText", product_name_tree
    )
    review_data["product_name"] = product_name

    # PRICING PART ###
    pricing = get_review_pricing(page)
    review_data["pricing"] = pricing

    # RATING PART ###
    rating = get_review_rating(page)
    review_data["rating"] = rating

    # USER REVIEWS PART ###
    user_reviews = get_users_reviews(page)
    review_data["user_reviews"] = user_reviews

    return review_data


def g2crowd_scrapper(url: str):
    with sync_playwright() as play:
        logging.info("Starting g2crowd scrapper for %s", url)
        time.sleep(2)
        try:
            browser = play.chromium.launch(headless=False, devtools=True)
            context = browser.new_context()
            page = context.new_page()
            time.sleep(1)
            review_data = get_review_data(page, url)
            return review_data
        except Exception as exception:
            logging.error("An error occurred: %s", exception)
            return None


def g2crowd_orchestrator():
    """
    This function will call the orchestrator that scraps g2crowd
    Output: g2crowd_output.json with all review data
    return: final_result with g2crowd review info as json
    """
    logging.info("Running g2crowd thread")
    start_time = time.time()
    relative_path = "g2crowd_input.csv"
    csv_input = os.path.join(script_dir, relative_path)
    csv_utility = CsvUtility()
    g2crowd_url_list = csv_utility.read_csv_file(csv_input)
    final_result = []
    for url in g2crowd_url_list:
        scrapper_data = g2crowd_scrapper(url)
        final_result.append(scrapper_data)

    # Output JSON with review data
    relative_path = "g2crowd_output.json"
    json_output = os.path.join(script_dir, relative_path)

    # Use json.dump() to write the data to a JSON file
    with open(json_output, "w", encoding="utf-8") as json_file:
        json.dump(final_result, json_file, indent=4)

    logging.info("Data has been written to %s", json_output)

    # Calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info("TIME TO EXECUTE G2CROWD_ORCHESTRATOR: %s", elapsed_time)
    return final_result
