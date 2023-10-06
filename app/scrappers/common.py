import csv
import logging
from app.exceptions import CustomException, ValidationException


class CsvUtility:
    def read_csv_file(self, file_path: str):
        try:
            logging.info("Reading csv file %s", file_path)
            with open(file_path, mode="r", newline="", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                result = []
                for row in csv_reader:
                    result.append(row[0])
                return result
        except FileNotFoundError as err:
            logging.error("File not found: %s, file_path", file_path)
            message = err.args[1]
            raise ValidationException(validation_message=message) from err
        except Exception as exception:
            logging.error("An exception occurred %s", exception)
            raise CustomException("An error occurred", 500) from exception

    def list_to_csv(self, _list, file_path):
        logging.info("Converting list to csv: %s", file_path)
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file)
                for url in _list:
                    csv_writer.writerow([url])
        except FileNotFoundError as err:
            logging.error("File not found: %s, file_path", file_path)
            message = err.args[1]
            raise ValidationException(validation_message=message) from err
        except Exception as exception:
            logging.error("An exception occurred %s", exception)
            raise CustomException("An error occurred", 500) from exception
