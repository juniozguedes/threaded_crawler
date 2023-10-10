from __future__ import print_function

import os.path
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))
credentials_input = os.path.join(script_dir, "credentials.json")


def parse_natural_language_query(natural_query):
    logging.info("Parsing natural language query %s", natural_query)
    # Split the query into parts
    parts = natural_query.split(", ")

    parsed_query = {"FILENAME": None, "TEXT": None}

    for part in parts:
        # Split each part into key and value
        try:
            key, value = part.split(" ", 1)
            key = key.upper()  # Convert key to uppercase
            if key in parsed_query:
                parsed_query[key] = value
            else:
                raise ValueError(f"Invalid keyword: {key}")
        except ValueError as value_error:
            # Handle the case where the split didn't result in exactly two values
            raise ValueError(f"Invalid query part: {part}") from value_error
    logging.info("Parsed query: %s", parsed_query)
    return parsed_query


def google_credentials():
    logging.info("Getting google_drive credentials from credentials.json")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_input, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds


def get_driver_items(creds, parsed_query):
    try:
        logging.info("Running get_driver_items to SELECT documents")
        service = build("drive", "v3", credentials=creds)

        filename_query = (
            f"name contains '{parsed_query['FILENAME']}'"
            if parsed_query["FILENAME"]
            else ""
        )
        text_query = (
            f"fullText contains '{parsed_query['TEXT']}'"
            if parsed_query["TEXT"]
            else ""
        )

        # Construct the final query
        final_query = " and ".join(filter(None, [filename_query, text_query]))
        results = (
            service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)", q=final_query)
            .execute()
        )
        items = results.get("files", [])

        if not items:
            logging.info("No files found")
        logging.info("Items found on driver: %s", items)
        return items

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
        return None


def google_drive_orchestrator(natural_query: str):
    """
    This function will call google drive API providing natural language queries:
    Example: "FILENAME Resumee, TEXT python experience"
    Explanation: In the example above, we search for a file with filename "Resumee" and inside text
    containing "python experience"
    Output: query print/log
    return: query print/log
    """
    logging.info("Running google_drive thread")
    creds = google_credentials()
    parsed_query = parse_natural_language_query(natural_query)
    items = get_driver_items(creds, parsed_query)
    return items
