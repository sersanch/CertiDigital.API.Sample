""" Module to tests the creation of a basic credential of assistance to an event... """
import json
import os
import unittest
from pathlib import Path
from certidigital import CertiDigitalException
from certidigital import CertiDigitalManager
from certidigital import CertiDigitalUtil


class TestBasicCredentialCreation(unittest.TestCase):
    """ Creates tests for a basic credential of assistance to an event...
        Credential contains just one activity and one diploma """

    __path_data = str(Path.home()) + "/PycharmProjects/TestCertiDigital/src/data/"

    @classmethod
    def setUpClass(cls):
        """ Delete entities stored on the previous run... """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        cls.__api_token = cm.get_token_from_api(auth_info["clientId"], auth_info["clientSecret"], auth_info["username"], auth_info["password"], auth_info["tokenUrl"])

        ids_file = cls.__path_data + "basiccredential/idlist.json"
        if not os.path.isfile(ids_file):
            print("File not found:  " + str(ids_file))
            return True
        util = CertiDigitalUtil()
        ids_deletion = util.read_data_from_json(ids_file, "r")
        cm = CertiDigitalManager()
        for credential in ids_deletion["credentials"]:
            credential_deletion_response = cm.delete_credential(credential, cls.__api_token["access_token"])
        for activity in ids_deletion["activities"]:
            activity_deletion_response = cm.delete_activity(activity, cls.__api_token["access_token"])
        return True

    @classmethod
    def tearDownClass(cls):
        """ Free resources (connections, files, etc...) """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        logout_response = cm.get_logged_out_from_api(auth_info["clientId"], auth_info["clientSecret"], cls.__api_token["access_token"], auth_info["logoutUrl"])
        print("Logout response code: " + logout_response)

    def test_basic_credential_ok(self):
        """ Creates a basic credential. One activity, one diploma and credential itself... """

        # Get logged user info...
        cm = CertiDigitalManager()
        user_info = cm.get_working_user_info(self.__api_token["access_token"])
        print("User info response: " + str(user_info))

        # Get issuing center info...
        issuing_centers_info = cm.get_issuing_center_info(self.__api_token["access_token"])
        # Though we get the info, we will use for tests always same issuing center
        issuing_center = 4
        print("Issuing centers info: " + str(issuing_centers_info))

        # 1. Get activities to create and call creation api endpoint...
        # 2. After creating activities link to awarding organization...
        util = CertiDigitalUtil()
        activities_json = util.read_data_from_json(self.__path_data + "/basiccredential/activities.json", "r")
        activities_ids = []
        for activity in activities_json:
            activity_creation_response = cm.create_new_activity(issuing_center, activity, self.__api_token["access_token"])
            print("Activity creation response: " + str(activity_creation_response))
            activities_ids.append(activity_creation_response["oid"])
            organization_relation_response = cm.rel_organization_to_activity(issuing_center, activity_creation_response["oid"], 3, self.__api_token["access_token"])
            print("Organization relation to activity response: " + str(organization_relation_response))

        # 1. Get credentials to create, link activities and call creation api endpoint...
        # 2. Link a diploma already created to the credential...
        credentials_json = util.read_data_from_json(self.__path_data + "/basiccredential/credentials.json", "r")
        credentials_ids = []
        for credential in credentials_json:
            credential["relPerformed"]["oid"] = activities_ids
            credential_creation_response = cm.create_new_credential(issuing_center, credential, self.__api_token["access_token"])
            print("Credential creation response: " + str(credential_creation_response))
            credentials_ids.append(credential_creation_response["oid"])
            diploma_relation_response = cm.rel_diploma_to_credential(issuing_center, credential_creation_response["oid"], 1, self.__api_token["access_token"])
            print("Diploma relation response: " + str(diploma_relation_response))

        # Store ids of entities created to be deleted on next run...
        ids_dict = {"activities": activities_ids, "credentials": credentials_ids}
        util.write_data_to_json(self.__path_data + "/basiccredential/idlist.json", ids_dict, "w")
