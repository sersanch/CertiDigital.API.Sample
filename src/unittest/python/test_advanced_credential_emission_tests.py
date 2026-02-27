""" Test for the emission of an advanced credential for a course with several subjects and assessments... """
import json
import time
import unittest
from pathlib import Path

from certidigital import CertiDigitalManager
from certidigital import CertiDigitalUtil


class TestAdvancedCredentialEmission(unittest.TestCase):
    """ Creates tests for a complex credential emission """

    __path_data = str(Path.home()) + "/PycharmProjects/CertiDigital.API.Sample/src/data"
    __path_output = str(Path.home()) + "/PycharmProjects/CertiDigital.API.Sample/src/unittest/output_files"

    @classmethod
    def setUpClass(cls):
        """ Get API token and set class attribute... """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        cls.__api_token = cm.get_token_from_api(auth_info["clientId"], auth_info["clientSecret"], auth_info["username"], auth_info["password"], auth_info["tokenUrl"])
        return True

    @classmethod
    def tearDownClass(cls):
        """ Free resources (connections, files, etc...) """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        logout_response = cm.get_logged_out_from_api(auth_info["clientId"], auth_info["clientSecret"], cls.__api_token["access_token"], auth_info["logoutUrl"])
        print("Logout response code: " + logout_response)

    def test_advanced_credential_issue(self):
        """ Issues digital credentials to recipients...
            Pre-requisites: 1. A credential template exists in the system. Specifically the one in the idlist.json file """

        # Get logged user info...
        cm = CertiDigitalManager()
        user_info = cm.get_working_user_info(self.__api_token["access_token"])
        print("User info response: " + str(user_info))

        # Get issuing center info (must be known in advance by the client app)...
        issuing_centers_info = cm.get_issuing_center_info(self.__api_token["access_token"])
        issuing_center = 1 #TEST
        #issuing_center = 2 #PRO
        print("Issuing centers info: " + str(issuing_centers_info))

        start_time = time.time()

        # 0. Identify the already created credential template to be used for issuance...
        util = CertiDigitalUtil()
        ids = util.read_data_from_json(self.__path_data + "/advancedcredential/idlist.json", "r")
        credential_id = ids["credentials"][0]

        # 1. Download the credential XLS template to be used for issuance (the fields are defined in the JSON template_body.json)...
        #    Fill downloaded XLS with recipients data (file EmissionRecipients.xls)...
        credential_template_response = cm.get_credential_template(issuing_center, credential_id, self.__api_token["access_token"])
        print("Credential template response: " + str(credential_template_response))
        dest_file_name = self.__path_data + "/advancedcredential/EmissionRecipientsTemplate.xls"
        with open(dest_file_name, 'wb') as file:
            file.write(credential_template_response.content)
        util = CertiDigitalUtil()
        result = util.fill_recipients_to_template()
        step_1_end = time.time()
        print(f"Time for step 1 (XLS template download and fill with recipients): {step_1_end - start_time:.2f} seconds")

        # 2. Issue the credential...
        file_name = self.__path_data + "/advancedcredential/EmissionRecipientsOutput.xls"
        credential_emission_response = cm.credentials_issue_through_template(issuing_center, credential_id, self.__api_token["access_token"], file_name)
        print("Credential emission response: " + str(credential_emission_response))
        step_2_end = time.time()
        elapsed = step_2_end - step_1_end
        print("Time for step 2 (emissión process for " + str(len(credential_emission_response)) + " recipients): " + str(round(elapsed, 2)) + " seconds...")

        # 3. Get the emission id (emission block) from the response...
        emissions_block_id = credential_emission_response[0]["emissionsBlockId"]
        emissions_block_response = cm.get_emissions_block_data(emissions_block_id, self.__api_token["access_token"])

        # 4. Unpack the treated credentials and call the seal process for the correctly issued ones...
        #    Notice that this process itself sends email to recipients and sends to CertiDigital & Europass wallets...
        emission_list = emissions_block_response["emissions"]
        print('Total credentials in emission block with id=' + str(emissions_block_id) + ': ' + str(len(emission_list)))
        uuid_list, num_seal_pending = util.process_emission_block_status(emissions_block_id, emission_list)
        credentials_seal_response = cm.seal_credentials(issuing_center, uuid_list, self.__api_token["access_token"])
        print("Credential seal response: " + str(credentials_seal_response))
        num_seal_pending = len(credentials_seal_response["emissions"])
        print('Total new credentials queued for sealing:' + str(num_seal_pending))
        step_3_end = time.time()
        print(f"Time for step 3 (send credentials to sealing queues): {step_3_end - step_2_end:.2f} seconds")

        # 5. Once the credentials are queued for sealing, iterate through the list to show status by calling endpoint of emission block status...
        while num_seal_pending != 0:
            emissions_block_response = cm.get_emissions_block_data(emissions_block_id, self.__api_token["access_token"])
            emission_list = emissions_block_response["emissions"]
            uuid_list, num_seal_pending = util.process_emission_block_status(emissions_block_id, emission_list)
            time.sleep(10)
        step_4_end = time.time()
        print(f"Time for step 4 (credentials sealing): {step_4_end - step_3_end:.2f} seconds")

        # 6. Download PDFs associated to sealed credentials...
        emissions_block_response = cm.get_emissions_block_data(emissions_block_id, self.__api_token["access_token"])
        print("Emission block data response:" + str(emissions_block_response))
        for credential in emissions_block_response["emissions"]:
            if credential["stateId"] == 2:
                # 6.1. Get the credential jsonld file...
                credential_details_response = cm.get_credential_details(credential["uuid"], self.__api_token["access_token"])
                jsonld_credential_file = credential_details_response["payload"]
                jsonld_data = json.loads(jsonld_credential_file)
                with open(self.__path_output + "/" + credential["uuid"] + ".jsonld", "w", encoding="utf-8") as jld_file:
                    json.dump(jsonld_data, jld_file, indent=4, ensure_ascii=False)
                # 6.2. Get the pdf file associated to the jsonld file and save to disk...
                credential_pdf_response = cm.get_credential_pdf(credential_details_response, self.__api_token["access_token"])
                if credential_pdf_response.status_code == 200:
                    with open(self.__path_output + "/" + credential["uuid"] + ".pdf", "wb") as pdf_file:
                        pdf_file.write(credential_pdf_response.content)
        step_5_end = time.time()
        print(f"Time for step 5 (credentials PDF download): {step_5_end - step_4_end:.2f} seconds")
