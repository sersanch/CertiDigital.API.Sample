""" MUtilities module for the resto of the CertiDigital software... """
import json
from pathlib import Path
from .certidigitalexception import CertiDigitalException


class CertiDigitalUtil:
    """ Main class to manage CertiDigital utilities... """

    def __init__(self):
        self.__path_data = str(Path.home()) + "/PycharmProjects/TestCertiDigital/src/data"

    def read_data_from_json(self, fi, mode):
        """ Opens input json file with data of the booking, checks formats and returns data... """
        try:
            with open(fi, encoding='UTF-8', mode=mode) as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise CertiDigitalException("Wrong file or file path")
        except json.JSONDecodeError:
            raise CertiDigitalException("Wrong json file format")
        return data

    def write_data_to_json(self, fi, data, mode):
        """ Opens output json file and dumps data with bookings... """
        try:
            with open(fi, encoding='UTF-8', mode=mode) as f:
                json.dump(data, f, indent=4)
        except FileNotFoundError as e:
            raise CertiDigitalException("Wrong file or file path") from e
        except json.JSONDecodeError as e:
            raise CertiDigitalException("JSON Decode Error - Wrong JSON Format") from e
        return data

    def get_api_info(self, api_list, api_id):
        """ Gets an occurrence from the api_list """
        for api in api_list:
            if api["apiId"] == api_id:
                return api