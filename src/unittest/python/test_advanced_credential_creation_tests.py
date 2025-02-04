""" Test for the creation of an advanced credential for a course with several subjects and assessments... """

import os
import unittest
from pathlib import Path
from certidigital import CertiDigitalManager
from certidigital import CertiDigitalUtil


class TestAdvancedCredentialCreation(unittest.TestCase):
    """ Creates tests for a complex credential of a subject in a grade.
        Credential contains an achievement, activities, assessment, learning outcomes and a diploma """

    __path_data = str(Path.home()) + "/PycharmProjects/TestCertiDigital/src/data/"

    @classmethod
    def setUpClass(cls):
        """ Get API Token for the session and Delete entities stored on the previous run... """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        cls.__api_token = cm.get_token_from_api(auth_info["clientId"], auth_info["clientSecret"], auth_info["username"], auth_info["password"], auth_info["tokenUrl"])

        ids_file = cls.__path_data + "advancedcredential/idlist.json"
        if not os.path.isfile(ids_file):
            print("File not found:  " + str(ids_file))
            return True
        util = CertiDigitalUtil()
        ids_deletion = util.read_data_from_json(ids_file, "r")
        cm = CertiDigitalManager()
        for credential in ids_deletion["credentials"]:
            credential_deletion_response = cm.delete_credential(credential, cls.__api_token["access_token"])
        for achievement in ids_deletion["achievements"]:
            achievement_deletion_response = cm.delete_achievement(achievement, cls.__api_token["access_token"])
        for activity in ids_deletion["activities"]:
            activity_deletion_response = cm.delete_activity(activity, cls.__api_token["access_token"])
        for assessment in ids_deletion["assessments"]:
            assessment_deletion_response = cm.delete_assessment(assessment, cls.__api_token["access_token"])
        for learning_outcome in ids_deletion["learningOutcomes"]:
            learning_outcome_deletion_response = cm.delete_learning_outcome(learning_outcome, cls.__api_token["access_token"])

        return True

    @classmethod
    def tearDownClass(cls):
        """ Free resources (connections, files, etc...) """
        util = CertiDigitalUtil()
        auth_info = util.read_data_from_json(cls.__path_data + "/auth.json", "r")
        cm = CertiDigitalManager()
        logout_response = cm.get_logged_out_from_api(auth_info["clientId"], auth_info["clientSecret"], cls.__api_token["access_token"], auth_info["logoutUrl"])
        print("Logout response code: " + logout_response)

    def test_advanced_credential_creation_ok(self):
        """ Creates an advanced credential... """

        # 1. Get logged user info to gather university and issuing Center ids...
        manager = CertiDigitalManager()
        cm = manager
        user_info = cm.get_working_user_info(self.__api_token["access_token"])
        university_id = 3
        print("User info response: " + str(user_info))

        # 1. Get issuing center info...Although for the tests we will use just issuing center 4...
        issuing_centers_info = cm.get_issuing_center_info(self.__api_token["access_token"])
        issuing_center = 4
        print("Issuing centers info: " + str(issuing_centers_info))

        # 1. Get activities to create and call creation api endpoint...
        # 2. After creating activities link to awarding organization (compulsory)...
        util = CertiDigitalUtil()
        activities_json = util.read_data_from_json(self.__path_data + "/advancedcredential/activities.json", "r")
        activities_ids = []
        for activity in activities_json:
            activity_creation_response = cm.create_new_activity(issuing_center, activity, self.__api_token["access_token"])
            print("Activity creation response: " + str(activity_creation_response))
            activities_ids.append(activity_creation_response["oid"])
            organization_relation_response = cm.rel_organization_to_activity(issuing_center, activity_creation_response["oid"], university_id, self.__api_token["access_token"])
            print("Awarding organization relation to activity response: " + str(organization_relation_response))

        # 1. Get assessments to create and call creation api endpoint...
        assessments_json = util.read_data_from_json(self.__path_data + "/advancedcredential/assessments.json", "r")
        assessments_ids = []
        for assessment in assessments_json:
            assessment_creation_response = cm.create_new_assessment(issuing_center, assessment, self.__api_token["access_token"])
            print("Assessment creation response: " + str(assessment_creation_response))
            assessments_ids.append(assessment_creation_response["oid"])

        # 1. Get learning outcomes to create and call creation api endpoint...
        learning_outcomes_json = util.read_data_from_json(self.__path_data + "/advancedcredential/learningOutcomes.json", "r")
        learning_outcomes_ids = []
        for learning_oucome in learning_outcomes_json:
            learning_outcome_creation_response = cm.create_new_learning_outcome(issuing_center, learning_oucome, self.__api_token["access_token"])
            print("Learning outcome creation response: " + str(learning_outcome_creation_response))
            learning_outcomes_ids.append(learning_outcome_creation_response["oid"])

        # 1. Get achievements to create and call creation api endpoint...
        # 2. Link the assessments to the achievements...
        # 3. Link the learning outcomes to the achievements...
        # 4. Link the activities to the achievements...
        # 5. Link the awarding organization to the achievements...
        achievements_json = util.read_data_from_json(self.__path_data + "/advancedcredential/achievements.json", "r")
        achievements_ids = []
        for achievement in achievements_json:
            achievements_creation_response = cm.create_new_achievement(issuing_center, achievement, self.__api_token["access_token"])
            print("Achievement creation response: " + str(achievements_creation_response))
            achievements_ids.append(achievements_creation_response["oid"])
            for assessment in assessments_ids:
                assessment_relation_response = cm.rel_assessment_to_achievement(issuing_center, achievements_creation_response["oid"], assessment, self.__api_token["access_token"])
                print("Assessment relation to achievement response: " + str(assessment_relation_response))
            learning_outcomes_relation_response = cm.rel_learning_outcome_to_achievement(issuing_center, achievements_creation_response["oid"], learning_outcomes_ids, self.__api_token["access_token"])
            print("Learning outcomes relation to achievement response: " + str(learning_outcomes_relation_response))
            activities_relation_response = cm.rel_activities_to_achievement(issuing_center, achievements_creation_response["oid"], activities_ids, self.__api_token["access_token"])
            print("Activities relation to achievement response: " + str(activities_relation_response))
            organization_relation_response = cm.rel_organization_to_achievement(issuing_center, achievements_creation_response["oid"], university_id, self.__api_token["access_token"])
            print("Awarding organization relation to achievement response: " + str(organization_relation_response))

        # 1. Get credentials to create, link activities and assessments, call creation api endpoint...
        # 2. Link a diploma already created to the credential...
        credentials_json = util.read_data_from_json(self.__path_data + "/advancedcredential/credentials.json", "r")
        credentials_ids = []
        for credential in credentials_json:
            credential["relPerformed"]["oid"] = activities_ids
            credential_creation_response = cm.create_new_credential(issuing_center, credential, self.__api_token["access_token"])
            print("Credential creation response: " + str(credential_creation_response))
            credentials_ids.append(credential_creation_response["oid"])
            for achievement in achievements_ids:
                achievement_relation_response = cm.rel_achievement_to_credential(issuing_center, credential_creation_response["oid"], achievement, self.__api_token["access_token"])
                print("Achievement relation response: " + str(achievement_relation_response))
            diploma_relation_response = cm.rel_diploma_to_credential(issuing_center, credential_creation_response["oid"], 17, self.__api_token["access_token"])
            print("Diploma relation response: " + str(diploma_relation_response))

        # Store ids of entities created to be deleted on next run...
        ids_dict = {"activities": activities_ids, "credentials": credentials_ids, "assessments": assessments_ids, "learningOutcomes": learning_outcomes_ids, "achievements": achievements_ids}
        util.write_data_to_json(self.__path_data + "/advancedcredential/idlist.json", ids_dict, "w")
