import csv
import os
import requests
from bs4 import BeautifulSoup

from app.exceptions import CustomException, ValidationException

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def google_search(query):
    # Set the URL for Google Search
    url = f"https://www.google.com/search?q={query}+linkedin"
    pattern = f"company/{query}"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all <a> (anchor) tags in the parsed HTML
        links = soup.find_all("a")

        # Iterate through the links and check for the pattern
        for link in links:
            href = link.get("href")
            if href and pattern in href:
                # Return the link when the pattern is found
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


def company_thread(csv_input):
    print("Running company csv thread")
    companies_list = read_csv_file(csv_input)
    linkedin_urls = []
    for company in companies_list:
        company_linkedin = google_search(company)
        linkedin_urls.append(company_linkedin)

    # Specify the CSV file path
    csv_file_path = "urls.csv"

    # Open the CSV file in write mode
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        # Create a CSV writer
        csv_writer = csv.writer(csv_file)

        # Write the header row if needed (e.g., 'URLs')
        # csv_writer.writerow(['URLs'])

        # Write each URL to a new row in the CSV file
        for url in linkedin_urls:
            csv_writer.writerow([url])

    print(f"URLs have been saved to {csv_file_path}")
