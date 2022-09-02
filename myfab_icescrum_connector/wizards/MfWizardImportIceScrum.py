# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import urllib2
import json
from openerp.exceptions import MissingError

API_ICESCRUM_ENDPOINT = "https://cloud.icescrum.com/ws/project/"
API_ICESCRUM_FEATURE_NAME = "feature"
API_ICESCRUM_STORY_NAME = "story"
API_ICESCRUM_TASK_NAME = "task"
SCRUM_TYPE_NAMES = ["Feature", "Story"]
API_ICESCRUM_STATES = ["Brouillon", "Brouillon", "A faire", "A faire", "En cours", "En cours", "Terminé", "Terminé"]


class MfWizardImportIceScrum(models.TransientModel):
    _name = "mf.wizard.import.icescrum"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    mf_icescrum_project_name = fields.Char(required=True, string="IceScrum project's name")
    mf_token = fields.Char(required=True, string="IceScrum user's token")

    # ===========================================================================
    # METHODS
    # ===========================================================================
    @api.multi
    def action_import_from_icescrum(self):
        self.delete_all_icescrum_events()
        self.create_icescrum_types(SCRUM_TYPE_NAMES)
        features_api_list = self.get_data_from_icescrum_api(API_ICESCRUM_FEATURE_NAME)
        self.create_feature_records_from_features_api_list(features_api_list)

    def delete_all_icescrum_events(self):
        icescrum_events_ids = self.env["calendar.event"].search([("type_id", "in", SCRUM_TYPE_NAMES)])
        icescrum_events_ids.unlink()

    def create_icescrum_types(self, type_names_list):
        for type_name in type_names_list:
            if not self.env["action.type"].search([("name", '=', type_name)]):
                self.env["action.type"].create({
                    "name": type_name,
                    "active": True,
                    "type": "plan"
                })

    def get_data_from_icescrum_api(self, data_name, data_id=None):
        data_endpoint = self.get_data_endpoint(data_name)
        if data_id:
            data_endpoint += '/' + str(data_id)
        request = urllib2.Request(url=data_endpoint, headers=self.get_headers())
        response = urllib2.urlopen(request)
        result_json = response.read().decode("utf-8")
        return json.loads(result_json)

    def get_data_endpoint(self, data_name):
        project_endpoint = API_ICESCRUM_ENDPOINT + self.mf_icescrum_project_name
        return project_endpoint + '/' + data_name

    def get_headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-icescrum-token": self.mf_token
        }

    def create_feature_records_from_features_api_list(self, features_api_list):
        action_type_feature_id = self.env["action.type"].search([("name", '=', "Feature")])
        stories_api_list = self.get_data_from_icescrum_api(API_ICESCRUM_STORY_NAME)
        tasks_api_list = self.get_data_from_icescrum_api(API_ICESCRUM_TASK_NAME)
        # Creating the features and their children stories
        for feature_api_dict in features_api_list:
            feature_creation_dict = self.get_action_event_creation_dict(feature_api_dict, action_type_feature_id)
            if feature_api_dict["stories_ids"]:
                feature_creation_dict["mf_event_stories_ids"] = self.get_stories_creation_tuples_list_by_ids(
                    feature_api_dict["stories_ids"],
                    stories_api_list,
                    tasks_api_list
                )
                feature_creation_dict["mf_scrum_duration"] = self.get_total_scrum_duration_from_stories_creation_list(
                    feature_creation_dict["mf_event_stories_ids"]
                )
            self.env["calendar.event"].create(feature_creation_dict)
        # Creating the remaining orphans stories (not attached to a feature)
        for story_api_dict in stories_api_list:
            self.env["calendar.event"].create(self.get_story_creation_dict(story_api_dict, tasks_api_list))

    def get_stories_creation_tuples_list_by_ids(self, searched_stories_ids_dicts, stories_api_list, tasks_api_list):
        stories_creation_list = []
        for story_id_dict in searched_stories_ids_dicts:
            story_id = story_id_dict["id"]
            story_api_dict_index, story_api_dict = self.get_story_api_dict_from_list_by_id(stories_api_list, story_id)
            stories_api_list.pop(story_api_dict_index)
            stories_creation_list.append((0, 0, self.get_story_creation_dict(story_api_dict, tasks_api_list)))
        return stories_creation_list

    @staticmethod
    def get_total_scrum_duration_from_stories_creation_list(stories_creation_tuples_list):
        total_stories_scrum_duration = 0.0
        for story_creation_tuple in stories_creation_tuples_list:
            total_stories_scrum_duration += story_creation_tuple[2]["mf_scrum_duration"]
        return total_stories_scrum_duration

    @staticmethod
    def get_story_api_dict_from_list_by_id(stories_api_list, story_id):
        for story_api_dict_index, story_api_dict in enumerate(stories_api_list):
            if story_api_dict["id"] == story_id:
                return story_api_dict_index, story_api_dict

    def get_story_creation_dict(self, story_api_dict, tasks_api_list):
        action_type_story_id = self.env["action.type"].search([("name", '=', "Story")])
        story_creation_dict = self.get_action_event_creation_dict(story_api_dict, action_type_story_id)
        story_creation_dict["mf_scrum_duration"] = self.get_story_scrum_duration(story_api_dict["id"], tasks_api_list)
        return story_creation_dict

    def get_action_event_creation_dict(self, icescrum_event_api_dict, icescrum_event_type_id):
        icescrum_event_creation_dict = {
            "name": icescrum_event_api_dict["name"],
            "mf_external_id": icescrum_event_api_dict["id"],
            "start_datetime": self.format_api_datetime(icescrum_event_api_dict["dateCreated"]),
            "user_id": self.env.user.id,
            "affected_user_id": self.env.user.id,
            "description": icescrum_event_api_dict["description"],
            "type_id": icescrum_event_type_id.id,
            "state_id": self.format_api_state(icescrum_event_api_dict["state"]),
        }
        if icescrum_event_api_dict["doneDate"]:
            icescrum_event_creation_dict["stop_datetime"] = self.format_api_datetime(icescrum_event_api_dict["doneDate"])
        else:
            icescrum_event_creation_dict["stop_datetime"] = self.format_api_datetime(icescrum_event_api_dict["dateCreated"])
        return icescrum_event_creation_dict

    @staticmethod
    def get_story_scrum_duration(story_id, tasks_api_list):
        story_scrum_duration = 0.0
        for task_api_dict in tasks_api_list:
            if task_api_dict["parentStory"] and task_api_dict["parentStory"]["id"] == story_id and task_api_dict["spent"]:
                story_scrum_duration += task_api_dict["spent"]
        return story_scrum_duration

    @staticmethod
    def format_api_datetime(api_datetime):
        datetime = api_datetime.replace('T', ' ')
        return datetime[:-1]

    def format_api_state(self, api_state):
        action_state_id = self.env["action.state"].search([("name", '=', API_ICESCRUM_STATES[api_state])], None, 1)
        return action_state_id.id

    @staticmethod
    def get_scrum_type_names():
        return SCRUM_TYPE_NAMES