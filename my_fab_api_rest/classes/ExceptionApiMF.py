# -*- coding: utf-8 -*-
from openerp import models, fields, api, http, _
from ExceptionMF import ExceptionMF

class ExceptionApiMF(ExceptionMF):

    def __init__(self, message=""):
        ExceptionMF.__init__(self, message)
