# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class stockmove(models.Model):
    _inherit = 'stock.move'

    def name_get(self):
        res = []
        for rec in self:
            name = "["+str(rec.default_code)+"] " + rec.product_id.name
            res.append((rec.id,name))
        return res