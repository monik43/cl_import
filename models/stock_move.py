# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class stockmove(models.Model):
    _inherit = 'stock.move'

    def name_get(self):
        res = []
        for rec in self:
            name = rec.product_id.name + " >> ["+str(rec.id)+"]"
            res.append((rec.id,name))
        return res