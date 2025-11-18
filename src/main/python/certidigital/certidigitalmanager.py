""" Main module to manage CertiDigital API operations. Includes the exposed methods... """

from pathlib import Path
import requests.exceptions
from requests_toolbelt import MultipartEncoder

from .certidigitalexception import CertiDigitalException
from .certidigitalutil import CertiDigitalUtil


class CertiDigitalManager:
    """ Main class to manage CertiDigital API operations... """

    def __init__(self):
        self.__path_data = str(Path.home()) + "/PycharmProjects/TestCertiDigital/src/data"
        util = CertiDigitalUtil()
        self.__all_apis_info = util.read_data_from_json(self.__path_data + "/params_api.json", "r")

    def get_token_from_api(self, client_id, client_secret, username, password, token_url):
        """ Gets the token from the API to be used in subsequent session calls... """
        try:
            payload = {'grant_type': 'password', 'username': username, 'password': password, 'scope': 'openid'}
            response = requests.post(token_url, data=payload, auth=(client_id, client_secret), timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise CertiDigitalException("Error invoking to obtain the token") from e

    def get_logged_out_from_api(self, client_id, client_secret, token, logout_url):
        """ Gets logged out from the API... """
        try:
            payload = {'client_id': client_id, "client_secret": client_secret, "refresh_token": token}
            response = requests.post(logout_url, params=payload, timeout=300)
            response.raise_for_status()
            return str(response.status_code)
        except requests.exceptions.RequestException as e:
            raise CertiDigitalException("Error invoking to logout from the API: " + str(response.status_code)) from e

    def call_get_api(self, api_url, api_params, api_data, token):
        """ Makes a post API call, to the url passed as a parameter and using the data and token provided... """
        try:
            api_call_headers = {'authorization': 'Bearer ' + token, 'accept': 'application/json', 'content-Type': 'application/json'}
            api_call_response = requests.get(api_url, params=api_params, json=api_data, headers=api_call_headers, timeout=30)
            api_call_response.raise_for_status()
            return api_call_response.json()
        except requests.exceptions.RequestException as e:
            print("Error: " + api_call_response.text)
            raise CertiDigitalException(f"Error calling get API: {e}") from e

    def call_post_api(self, api_url, accept, content, api_params, api_data, token):
        """ Makes a post API call, to the url passed as a parameter and using the data and token provided... """
        try:
            accept_header = 'application/json'
            if accept != '':
                accept_header = accept
            content_type = 'application/json'
            if content != '':
                content_type = content
            api_call_headers = {'authorization': 'Bearer ' + token, 'accept': accept_header, 'Content-Type': content_type}
            print("Headers: " + str(api_call_headers))
            if content_type == 'application/json':
                api_call_response = requests.post(api_url, params=api_params, json=api_data, headers=api_call_headers, timeout=3600)
            else:
                api_call_response = requests.post(api_url, params=api_params, data=api_data, headers=api_call_headers, timeout=3600)
            api_call_response.raise_for_status()
            if accept_header == 'application/json':
                return api_call_response.json()
            else:
                return api_call_response
        except requests.exceptions.RequestException as e:
            print("Error: " + api_call_response.text)
            raise CertiDigitalException(f"Error calling post API: {e}") from e

    def call_delete_api(self, api_url, api_params, api_data, token):
        """ Makes a delete API call, to the url passed as a parameter and using the data and token provided... """
        try:
            api_call_headers = {'authorization': 'Bearer ' + token, 'accept': 'application/json', 'content-Type': 'application/json'}
            api_call_response = requests.delete(api_url, params=api_params, json=api_data, headers=api_call_headers, timeout=30)
            api_call_response.raise_for_status()
            return str(api_call_response.status_code)
        except requests.exceptions.RequestException as e:
            print("Delete result: " + str(api_call_response.status_code) + ": " + api_call_response.text)
            return ""

    def get_working_user_info(self, token):
        """ Gets working user info... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "getUserInfo")
        json_response = self.call_get_api(api_info["apiUrl"], "", "", token)
        return json_response

    def get_issuing_center_info(self, token):
        """ Gets issuing centers info... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "getIssuingCentersInfo")
        json_response = self.call_get_api(api_info["apiUrl"], "", "", token)
        return json_response

    def get_organizations_info(self, token):
        """ Gets organizations info... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "getOrganizationsInfo")
        json_response = self.call_get_api(api_info["apiUrl"], "", "", token)
        return json_response

    def create_new_activity(self, issuing_center_id, request_body, token):
        """ Creates a new activity in the issuing center based on request body parameters... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createActivity")
        api_params = "issuingCenterId=" + str(issuing_center_id)
        json_response = self.call_post_api(api_info["apiUrl"], '', '', api_params, request_body, token)
        return json_response

    def delete_activity(self, activity_id, token):
        """ Deletes an unused activity... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "deleteActivity")
        print("Deleting activity with id: " + str(activity_id))
        json_response = self.call_delete_api(api_info["apiUrl"] + "/" + str(activity_id), "", "", token)
        print("Deleted activity (response code: " + json_response + ")")
        return json_response

    def rel_organization_to_activity(self, issuing_center_id, activity_id, organization_id, token):
        """ Relates am organization with an activity... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createActivity")
        api_url = api_info["apiUrl"] + "/" + str(activity_id) + "/awardingBody"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [organization_id], "singleOid": organization_id}
        print("Relating activity " + str(activity_id) + " and organization " + str(organization_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def create_new_credential(self, issuing_center_id, request_body, token):
        """ Creates a new credential in the issuing center based on request body parameters... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createCredential")
        api_params = "issuingCenterId=" + str(issuing_center_id)
        json_response = self.call_post_api(api_info["apiUrl"], '', '', api_params, request_body, token)
        return json_response

    def delete_credential(self, credential_id, token):
        """ Deletes an unused credential... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "deleteCredential")
        print("Deleting credential with id: " + str(credential_id))
        json_response = self.call_delete_api(api_info["apiUrl"] + "/" + str(credential_id), "", "", token)
        print("Deleted credential (response code: " + json_response + ")")
        return json_response

    def rel_diploma_to_credential(self, issuing_center_id, credential_id, diploma_id, token):
        """ Relates a diploma to a credential... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createCredential")
        api_url = api_info["apiUrl"] + "/" + str(credential_id) + "/diploma"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [diploma_id], "singleOid": diploma_id}
        print("Relating credential " + str(credential_id) + " and diploma " + str(diploma_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def rel_achievement_to_credential(self, issuing_center_id, credential_id, achievement_id, token):
        """ Relates an achievement to a credential... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createCredential")
        api_url = api_info["apiUrl"] + "/" + str(credential_id) + "/achieved"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [achievement_id], "singleOid": achievement_id}
        print("Relating credential " + str(credential_id) + " and achievement " + str(achievement_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def get_credential_template(self, issuing_center_id, credential_id, token):
        """ Calls API to gather the credential XLS template to fill with credential recipients... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createCredential")
        api_url = api_info["apiUrl"] + "/" + str(credential_id) + "/recipients/templates"
        api_params = {"issuingCenterId": str(issuing_center_id), "locale": "es"}
        util = CertiDigitalUtil()
        base_template_json = util.read_data_from_json(self.__path_data + "/advancedcredential/template_body.json", "r")
        request_body = base_template_json
        print("RB: " + str(request_body))
        print("Getting credential XLS template for credential: " + str(credential_id))
        json_response = self.call_post_api(api_url, 'application/octet-stream', '', api_params, request_body, token)
        return json_response

    def credentials_issue_through_template(self, issuing_center_id, credential_id, token, file_name):
        """ Calls API to issue the credentials through an XLS template already filled with the recipients... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createCredential")
        api_url = api_info["apiUrl"] + "/" + str(credential_id) + "/issue/templates"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        api_params = api_params + "&alias=" + "None"
        print("Emission process being done for credential: " + str(credential_id))
        with open(file_name, 'rb') as file:
            multipart_data = MultipartEncoder(
                fields={
                    'file': (file_name, file, 'application/vnd.ms-excel')
                }
            )
            json_response = self.call_post_api(api_url, 'application/json', multipart_data.content_type, api_params, multipart_data, token)
            return json_response

    def get_emissions_block_data(self, emissions_block_id, token):
        """ Gets the detailed info associated with an emission block... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "getEmissionsBlockData")
        api_url = api_info["apiUrl"] + "/" + str(emissions_block_id)
        json_response = self.call_get_api(api_url, "", "", token)
        return json_response

    def seal_credentials(self, issuing_center_id, uuids_list, token):
        """ Tries to seal the identified credential list of uuids... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "emissionsSeal")
        api_url = api_info["apiUrl"]
        api_params = ''
        request_body = {'uuidList': uuids_list, 'issuingCenterId': issuing_center_id}
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def send_credentials(self, issuing_center_id, uuids_list, token):
        """ Send email to the identified credential list of uuids... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "emissionsSend")
        api_url = api_info["apiUrl"]
        api_params = ''
        request_body = {'uuidList': uuids_list}
        print("Send email process being done for " + str(len(uuids_list)) + " recipients. List is: " + str(uuids_list))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def send_credentials_to_euwallet(self, issuing_center_id, uuids_list, token):
        """ Send email to the identified credential list of uuids... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "emissionsSendEUWallet")
        api_url = api_info["apiUrl"]
        for uuid in uuids_list:
            api_params = {"id": str(issuing_center_id), "uuid": "es"}
            request_body = ''
            print("Send to Europass process being done for " + uuid + " recipient...")
            json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
            print(json_response)
        return True

    def create_new_assessment(self, issuing_center_id, request_body, token):
        """ Creates a new assessment in the issuing center based on request body parameters... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAssessment")
        api_params = "issuingCenterId=" + str(issuing_center_id)
        json_response = self.call_post_api(api_info["apiUrl"], '', '', api_params, request_body, token)
        return json_response

    def delete_assessment(self, assessment_id, token):
        """ Deletes an unused assessment... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "deleteAssessment")
        print("Deleting assessment with id: " + str(assessment_id))
        json_response = self.call_delete_api(api_info["apiUrl"] + "/" + str(assessment_id), "", "", token)
        print("Deleted assessment (response code: " + json_response + ")")
        return json_response

    def rel_organization_to_assessment(self, issuing_center_id, assessment_id, organization_id, token):
        """ Relates am organization with an assessment... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAssessment")
        api_url = api_info["apiUrl"] + "/" + str(assessment_id) + "/awardingBody"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [organization_id], "singleOid": organization_id}
        print("Relating assessment " + str(assessment_id) + " and organization " + str(organization_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def create_new_learning_outcome(self, issuing_center_id, request_body, token):
        """ Creates a new learning outcome in the issuing center based on request body parameters... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createLearningOutcome")
        api_params = "issuingCenterId=" + str(issuing_center_id)
        json_response = self.call_post_api(api_info["apiUrl"], '', '', api_params, request_body, token)
        return json_response

    def delete_learning_outcome(self, learning_outcome_id, token):
        """ Deletes an unused assessment... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "deleteLearningOutcome")
        print("Deleting learning outcome with id: " + str(learning_outcome_id))
        json_response = self.call_delete_api(api_info["apiUrl"] + "/" + str(learning_outcome_id), "", "", token)
        print("Deleted learning outcome (response code: " + json_response + ")")
        return json_response

    def create_new_achievement(self, issuing_center_id, request_body, token):
        """ Creates a new achievement in the issuing center based on request body parameters... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAchievement")
        api_params = "issuingCenterId=" + str(issuing_center_id)
        json_response = self.call_post_api(api_info["apiUrl"], '', '', api_params, request_body, token)
        return json_response

    def delete_achievement(self, achievement_id, token):
        """ Deletes an achievement... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "deleteAchievement")
        print("Deleting achievement with id: " + str(achievement_id))
        json_response = self.call_delete_api(api_info["apiUrl"] + "/" + str(achievement_id), "", "", token)
        print("Deleted achievement (response code: " + json_response + ")")
        return json_response

    def rel_assessment_to_achievement(self, issuing_center_id, achievement_id, assessment_id, token):
        """ Relates am organization with an activity... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAchievement")
        api_url = api_info["apiUrl"] + "/" + str(achievement_id) + "/provenBy"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [assessment_id], "singleOid": assessment_id}
        print("Relating achievement " + str(achievement_id) + " and assessment " + str(assessment_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def rel_learning_outcome_to_achievement(self, issuing_center_id, achievement_id, learning_outcome_ids, token):
        """ Relates some learning outcomes with an achievement... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAchievement")
        api_url = api_info["apiUrl"] + "/" + str(achievement_id) + "/learningOutcomes"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": learning_outcome_ids, "singleOid": 0}
        print("Relating achievement " + str(achievement_id) + " and learning outcomes " + str(learning_outcome_ids))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def rel_activities_to_achievement(self, issuing_center_id, achievement_id, activities_ids, token):
        """ Relates some activities with an achievement... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAchievement")
        api_url = api_info["apiUrl"] + "/" + str(achievement_id) + "/influencedBy"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": activities_ids, "singleOid": 0}
        print("Relating achievement " + str(achievement_id) + " and activities " + str(activities_ids))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

    def rel_organization_to_achievement(self, issuing_center_id, achievement_id, organization_id, token):
        """ Relates some organization with an achievement... """
        util = CertiDigitalUtil()
        api_info = util.get_api_info(self.__all_apis_info, "createAchievement")
        api_url = api_info["apiUrl"] + "/" + str(achievement_id) + "/awardingBody"
        api_params = "issuingCenterId=" + str(issuing_center_id)
        request_body = {"oid": [organization_id], "singleOid": organization_id}
        print("Relating achievement " + str(achievement_id) + " and organization " + str(organization_id))
        json_response = self.call_post_api(api_url, '', '', api_params, request_body, token)
        return json_response

