# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, modules
from datetime import date
import logging

logger = logging.getLogger(__name__)


class DataInitializerMyFabMF(models.Model):
    _inherit = "data.initializer.mf"
    _name = "data.initializer.myfab.mf"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    launch_base_init = fields.Boolean(string="Launch base initialization", default=False)
    launch_data_recovery_templates_init = fields.Boolean(string="Launch data recovery templates initialization",
                                                         default=False)
    launch_modules_init = fields.Boolean(string="Launch Open-Prod modules initialization", default=True, readonly=True)
    launch_dev_tools_init = fields.Boolean(string="Launch advanced development tools initialization", default=True,
                                           readonly=True)

    # ===========================================================================
    # GENERAL METHODS
    # ===========================================================================
    @api.multi
    def display_wizard(self):
        logger.info("Displaying MyFab Base Initialization wizard")

    @staticmethod
    def get_models_to_overwrite_names():
        return ["excel.import"]

    def get_models_to_avoid_names(self):
        models_to_avoid_names_list = []
        if not self.launch_base_init:
            models_to_avoid_names_list += [
                "account.invoicing.method", "payment.method", "stock.alert.color", "stock.location"
            ]
        if not self.launch_data_recovery_templates_init:
            models_to_avoid_names_list += ["excel.import"]
        if not self.launch_base_init and not self.launch_data_recovery_templates_init:
            models_to_avoid_names_list += ["ir.model.fields"]
        return models_to_avoid_names_list

    def set_configurations(self):
        if self.launch_base_init:
            self.configure_admin_user()
            self.configure_companies()
            self.configure_stock_settings()
            self.configure_calendar()

    def configure_admin_user(self):
        logger.info("Configuring the admin user")
        admin_user = self.env["res.users"].search([("login", '=', "admin")], None, 1)
        groups = self.env["res.groups"].search([])
        if not self.is_user_in_all_groups(admin_user, groups):
            self.add_user_to_all_groups(admin_user, groups)
        if admin_user.lang != "fr_FR":
            admin_user.lang = "fr_FR"
        if admin_user.tz != "Europe/Paris":
            admin_user.tz = "Europe/Paris"

    @staticmethod
    def is_user_in_all_groups(user, groups):
        return len(groups) <= len(user.groups_id)

    @staticmethod
    def add_user_to_all_groups(user, groups):
        for group in groups:
            if user not in group.users:
                group.users = [(4, user.id)]

    def configure_companies(self):
        logger.info("Configuring the companies")
        companies = self.env["res.company"].search([])
        for company in companies:
            if not company.warehouse_id:
                warehouse = self.env["stock.warehouse"].search([], None, 1)
                company.write({
                    "warehouse_id": warehouse.id,
                    "horizon": 50
                })

    def configure_stock_settings(self):
        logger.info("Configuring the stock settings")
        stock_setting = self.env["stock.config.settings"].search([], None, 1)
        stock_setting.write({
            "min_horizon": 50,
            "manage_picking_document": True,
            "procurement_consider_purchase": True,
            "is_compute_wo_prices_at_closing": True,
            "procurement_consider_mo": True
        })

    def configure_calendar(self):
        logger.info("Configuring the calendar")
        calendar_template = self.env["calendar.template"].search([], None, 1)
        calendar_template.name = "Général"
        current_year = date.today().year
        wizard_create_template_lines = self.with_context({}).env["wizard.create.template.lines"].create({
            "calendar_template_id": calendar_template.id,
            "start_date": date(current_year, 1, 1),
            "end_date": date(current_year + 3, 12, 31),
            "frequency": 1,
            "hour_start0": 8,
            "hour_start1": 8,
            "hour_start2": 8,
            "hour_start3": 8,
            "hour_start4": 8,
            "hour_end0": 18,
            "hour_end1": 18,
            "hour_end2": 18,
            "hour_end3": 18,
            "hour_end4": 18,
            "hour_number0": 8,
            "hour_number1": 8,
            "hour_number2": 8,
            "hour_number3": 8,
            "hour_number4": 8
        })
        wizard_create_template_lines.generate_lines()
