# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'document_type':fields.selection([('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO')],'PO Document Type'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date'),        
                }
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        invoice_vals = super(stock_picking,self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
        if picking.type=='in':
            invoice_vals.update({
                             'origin': picking.name or '',
                             })
        return invoice_vals
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {
        'document_type':fields.selection([('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO')],'PO Document Type'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date'),   
                }
    
stock_picking_in()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    _columns = {
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')],'Action to be Taken'),
        'po_indent_id': fields.many2one('tpt.purchase.indent','PO Indent No'),   
                }
    
stock_move()
