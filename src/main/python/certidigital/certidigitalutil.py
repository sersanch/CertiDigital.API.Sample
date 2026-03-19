""" MUtilities module for the resto of the CertiDigital software... """
import json
from pathlib import Path

import xlwt
import pandas as pd

from .certidigitalexception import CertiDigitalException


class CertiDigitalUtil:
    """ Main class to manage CertiDigital utilities... """

    def __init__(self):
        self.__path_data = str(Path.home()) + "/PycharmProjects/CertiDigital.API.Sample/src/data"

    def read_data_from_json(self, fi, mode):
        """ Opens input json file with data of the booking, checks formats and returns data... """
        try:
            with open(fi, encoding='UTF-8', mode=mode) as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise CertiDigitalException("Wrong file or file path") from e
        except json.JSONDecodeError as e:
            raise CertiDigitalException("Wrong json file format") from e
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
        return None

    def fill_recipients_to_template(self):
        """ Copies the data inside EmissionRecipients.xls into the EmissionRecipientsTemplate.xls file"""
        recipients_file_name = self.__path_data + "/advancedcredential/EmissionRecipients.xls"
        recipients_df = pd.read_excel(recipients_file_name, skiprows=4, header=None)
        template_file_name = self.__path_data + "/advancedcredential/EmissionRecipientsTemplate.xls"
        destination_df = pd.read_excel(template_file_name, header=None)
        destination_file_name = self.__path_data + "/advancedcredential/EmissionRecipientsOutput.xls"
        wb = xlwt.Workbook()
        sheet = wb.add_sheet('data')
        for row_num, row in destination_df.iterrows():
            for col_num, value in enumerate(row):
                sheet.write(row_num, col_num, value)
        for row_num, row in recipients_df.iterrows():
            for col_num, value in enumerate(row):
                sheet.write(row_num + 4, col_num, value)
        wb.save(destination_file_name)
        return True

    def split_recipients_output(self, file_name, block_size, header_rows=4):
        """ Splits EmissionRecipientsOutput.xls into chunks of block_size recipients (keeps header rows). """
        if block_size < 1:
            raise CertiDigitalException("Emission block size must be >= 1")
        data_df = pd.read_excel(file_name, header=None)
        if data_df.empty:
            return [file_name]
        header_df = data_df.iloc[:header_rows]
        recipients_df = data_df.iloc[header_rows:]
        if recipients_df.empty:
            return [file_name]
        base_path = Path(file_name)
        chunk_files = []
        chunk_index = 1
        for chunk_start in range(0, len(recipients_df), block_size):
            chunk_df = recipients_df.iloc[chunk_start:chunk_start + block_size]
            wb = xlwt.Workbook()
            sheet = wb.add_sheet('data')
            for row_num, row in enumerate(header_df.itertuples(index=False, name=None)):
                for col_num, value in enumerate(row):
                    sheet.write(row_num, col_num, value)
            for row_num, row in enumerate(chunk_df.itertuples(index=False, name=None)):
                for col_num, value in enumerate(row):
                    sheet.write(row_num + header_rows, col_num, value)
            chunk_file = str(base_path.with_name(f"{base_path.stem}_part{chunk_index}{base_path.suffix}"))
            wb.save(chunk_file)
            chunk_files.append(chunk_file)
            chunk_index += 1
        return chunk_files

    def process_emission_block_status(self, emission_block_id, emission_block):
        """ Handles the emission block status report... """
        status_map = {1: "Issued (not sealed)", 2: "Sealed", 3: "Rejected", 4: "Issued with error", 5: "Duplicated", 6: "Re-Issued",
                      7: "Sealed with error", 8: "Sent with error", 9: "Sent with error (EU)", 10: "Queued for sealing",
                      11: 'Queued for sending', 12: "Sent to validation", 13: "No status"}
        status_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        uuid_list = []
        for emission in emission_block:
            status_count[(emission.get("stateId") or 13) - 1] = status_count[(emission.get("stateId") or 13) - 1] + 1
            uuid_list.append(emission["uuid"])
        print("-------- Credentials block status report: BLOCK_ID = " + str(emission_block_id) + " --------")
        for status in status_map:
            if status_count[status-1] != 0:
                print(status_map[status] + ": " + str(status_count[status-1]))
        print("-----------------------------------------------------------------")
        return uuid_list, status_count[9] #+status_count[8]+status_count[7]+status_count[10]
