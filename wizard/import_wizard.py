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
    
    origin = fields.Char()
    products_move = fields.One2many('stock.move','picking_id')
    product = fields.Many2one('stock.move', "Producto a procesar", domain="[('origin','=',origin)]")
    file_import = fields.Binary("Archivo a importar")

    

    @api.model
    def default_get(self, fields):
        res = super(ImportFile, self).default_get(fields)
        stock_picking = self.env['stock.picking'].browse(self._context.get('active_ids',[]))
        res.update({'origin': stock_picking.origin})
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
            if row_no != 0:
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode(
                    'utf-8') or str(row.value), sheet.row(row_no)))
                values.update({'lot_id': line[0]})
                res = self.create_move_lines(values)
                
        return res

    @api.multi
    def create_move_lines(self, values):
        res = self.env['stock.move'].browse(self._context.get('active_ids',[]))
        if values.get("lot_id"):
            s = str(values.get("lot_id"))
            lot_id = s.rstrip('0').rstrip('.') if '.' in s else s
            res.update({'move_line_nosuggest_ids':[(0,0, {'name':str(lot_id),'lot_id': lot_id, 'qty_done':1, 'product_uom_id':1,'location_id':self.product.location_id,'location_dest_id':self.product.location_dest_id})]})