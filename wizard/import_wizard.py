# -*- coding: utf-8 -*-

import io
import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
_logger = logging.getLogger(__name__)
try:
    import xlwt
except ImportError:
    print('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    print('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    print('Cannot `import base64`.')


class ImportFile(models.TransientModel):
    _name = "cl.import.file"
    
    products_move = fields.One2many('stock.move','picking_id')
    product = fields.Many2one('stock.move')
    file_import = fields.Binary(string="Archivo a importar")

    @api.model
    def default_get(self, fields):
        res = super(ImportFile, self).default_get(fields)
        stock_picking = self.env['stock.picking'].browse(self._context.get('active_ids',[]))
        vals = []
        for product_line in stock_picking.move_lines:
            vals.append((4,product_line.id))
        print(vals)
        res.update({'products_move': [(4, 18984), (4, 18985)]})
        return res

    @api.multi
    def import_file(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file_import))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

        except:
            raise Warning(_("Archivo inválido"))

        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row: row.value.encode(
                    'utf-8'), sheet.row(row_no))
                print(fields)
            else:

                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode(
                    'utf-8') or str(row.value), sheet.row(row_no)))
                values.update({'name': line[0]})
                #res = self.create_chart_accounts(values)
                for val in values:
                    print(val, ": ", values[val])
        #return res

    @api.multi
    def create_chart_accounts(self,values):

        if values.get("code") == "":
            raise Warning(_('Code field cannot be empty.') )

        if values.get("name") == "":
            raise Warning(_('Name Field cannot be empty.') )

        if values.get("user") == "":
            raise Warning(_('Type field cannot be empty.'))

        if values.get("code"):
            s = str(values.get("code"))
            code_no = s.rstrip('0').rstrip('.') if '.' in s else s

        account_obj = self.env['account.account']
        account_search = account_obj.search([
            ('code', '=', values.get('code'))
            ])

        
        is_reconcile = False
        is_deprecated= False

        if values.get("reconcile") == 'TRUE' or values.get("reconcile") == "1":
                is_reconcile = True

        if values.get("deprecat") == 'TRUE' or values.get("deprecat") == "1":
                is_deprecated = True

        user_id = self.find_user_type(values.get('user'))
        currency_get = self.find_currency(values.get('currency'))
        group_get = self.find_group(values.get('group'))

        

# --------tax-
        tax_ids = []
        if values.get('tax'):
            if ';' in  values.get('tax'):
                tax_names = values.get('tax').split(';')
                for name in tax_names:
                    tax= self.env['account.tax'].search([('name', '=', name)])
                    if not tax:
                        raise Warning(_('%s Tax not in your system') % name)
                    for t in tax:
                        tax_ids.append(t)

            elif ',' in  values.get('tax'):
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax= self.env['account.tax'].search([('name', '=', name)])
                    if not tax:
                        raise Warning(_('%s Tax not in your system') % name)
                    for t in tax:
                        tax_ids.append(t)
            else:
                tax_names = values.get('tax').split(',')
                tax= self.env['account.tax'].search([('name', '=', tax_names)])
                if not tax:
                    raise Warning(_('%s Tax not in your system') % tax_names)
                for t in tax:
                    tax_ids.append(t)

# ------------tags
        tag_ids = []
        if values.get('tag'):
            if ';' in  values.get('tag'):
                tag_names = values.get('tag').split(';')
                for name in tag_names:
                    tag= self.env['account.account.tag'].search([('name', '=', name)])
                    if not tag:
                        raise Warning(_('%s Tag not in your system') % name)
                    tag_ids.append(tag)

            elif ',' in  values.get('tag'):
                tag_names = values.get('tag').split(',')
                for name in tag_names:
                    tag= self.env['account.account.tag'].search([('name', '=', name)])
                    if not tag:
                        raise Warning(_('%s Tag not in your system') % name)
                    tag_ids.append(tag)
            else:
                tag_names = values.get('tag').split(',')
                tag= self.env['account.account.tag'].search([('name', '=', tag_names)])
                if not tag:
                    raise Warning(_('%s Tag not in your system') % tag_names)
                tag_ids.append(tag)

        abc = {
                'code' : code_no,
                'name' : values.get('name'),
                'user_type_id':user_id.id,
                'tax_ids':[(6,0,[y.id for y in tax_ids])]if values.get('tax') else False,	
                'tag_ids':[(6,0,[x.id for x in tag_ids])]if values.get('tag') else False,
                'group_id':group_get.id,
                'currency_id':currency_get or False,
                'reconcile':is_reconcile,
                'deprecated':is_deprecated,
        }
        chart_id = account_obj.create(abc)		

        return chart_id


# ---------------------------user-----------------

    @api.multi
    def find_user_type(self,user):
        user_type=self.env['account.account.type']
        user_search = user_type.search([('name','=',user)])

        if user_search:
            return user_search

        else:
            raise Warning(_('Field User is not correctly set.'))

# --------------------currency------------------

    @api.multi
    def find_currency(self, name):
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search.id
        else:
            if name == "":
                pass
            else:
                raise Warning(_(' %s currency are not available.') % name)

# -----------------group-------

    @api.multi
    def find_group(self,group):
        group_type=self.env['account.group']
        group_search = group_type.search([('name','=',group)])

        if group_search:
            return group_search
        else:
            group_id = group_type.create({
                'name' : group
                })
            return group_id
