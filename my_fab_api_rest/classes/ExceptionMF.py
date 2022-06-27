# -*- coding: utf-8 -*-
from openerp import models, fields, api, http, _

class ExceptionMF():
    __stack = []

    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return "message : "+{self.message}

    def __repr__(self):
        return "message : "+{self.message}
