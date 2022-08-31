# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import urllib2
import json
from openerp.exceptions import MissingError

API_ICESCRUM_ENDPOINT = "https://cloud.icescrum.com/ws/project/"
API_ICESCRUM_FEATURE_NAME = "feature"
API_ICESCRUM_STORY_NAME = "story"
SCRUM_TYPE_NAMES = ["Feature"]


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
        self.create_icescrum_types(SCRUM_TYPE_NAMES)
        features_api_list = self.get_data_from_icescrum_api(API_ICESCRUM_FEATURE_NAME)
        # print(features_api_list)
        self.create_feature_records_from_features_api_list(features_api_list)

    def create_icescrum_types(self, type_names_list):
        for type_name in type_names_list:
            if not self.env["action.type"].search([("name", '=', type_name)]):
                self.env["action.type"].create({
                    "name": type_name,
                    "active": True,
                    "type": "do_list"
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
        resource_id = self.env["mrp.resource"].search([("name", '=', "IceScrum")], None, 1)
        if not resource_id:
            calendar_id = self.env["calendar"].search([], None, 1)
            if not calendar_id:
                raise MissingError(_("Please create a calendar before importing."))
            pause_id = self.env["resource.pause"].search([], None, 1)
            if not calendar_id:
                raise MissingError(_("Please create a resource.pause before importing."))
            resource_id = self.env["mrp.resource"].create({
                "name": "IceScrum",
                "calendar_id": calendar_id.id,
                "active": True,
                "type": "human",
                "pause_id": pause_id.id,
                "opening_time": 9.0,
                "offset": 1,
                "factor": 2,
            })
        print(resource_id)
        for feature_api_dict in features_api_list:
            feature_creation_dict = {
                "name": feature_api_dict["name"],
                "start_datetime": self.format_api_datetime(feature_api_dict["dateCreated"]),
                "stop_datetime": self.format_api_datetime(feature_api_dict["doneDate"]) if feature_api_dict["doneDate"] else "2999-12-31",
                "user_id": self.env.user.id,
                "affected_user_id": self.env.user.id,
                "description": feature_api_dict["description"],
                "type_id": action_type_feature_id.id
            }
            if feature_api_dict["stories_ids"]:
                feature_creation_dict["timetracking_ids"] = []
            for story_api_id_dict in feature_api_dict["stories_ids"]:
                story_creation_dict = self.get_story_creation_dict_from_id(story_api_id_dict["id"])
                story_creation_dict["resource_id"] = resource_id.id
                feature_creation_dict["timetracking_ids"].append((0, 0, story_creation_dict))
            print("****")
            print(feature_creation_dict)
            self.env["calendar.event"].create(feature_creation_dict)

    @staticmethod
    def format_api_datetime(api_datetime):
        datetime = api_datetime.replace('T', ' ')
        return datetime[:-1]

    def get_story_creation_dict_from_id(self, story_api_id):
        story_api_dict = self.get_data_from_icescrum_api(API_ICESCRUM_STORY_NAME, story_api_id)
        start_date_formatted = self.format_api_datetime(story_api_dict["dateCreated"])
        return {
            "name": story_api_dict["name"],
            "comment": story_api_dict["description"],
            "user_id": self.env.user.id,
            "company_id": self.env.user.company_id.id,
            "start_date": start_date_formatted,
            "time": 1,
            "time_spent": 1,
            "hourly_cost": 0.0,
            "end_date": self.format_api_datetime(story_api_dict["doneDate"]) if story_api_dict["doneDate"] else start_date_formatted,
        }