# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True),
#         'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order',required = True),
        'so_date':fields.date('SO Date'),
        'po_date':fields.date('PO Date'),
        'document_type':fields.selection([('saleorder','Sale Order'),('return','Return Sales Order'),('scrap','Scrap Sales')],'Document Type' ,required=True),
        'po_number':fields.float('PO Number', size = 1024),
        'reason':fields.text('Reason'),
        'quotaion_no':fields.float('Quotaion No', size = 1024),
        'expected_date':fields.date('Expected delivery Date'),
        'document_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status' ,required=True),
        'incoterms_id':fields.many2one('stock.incoterms','Incoterms',required = True),
        'distribution_chanel':fields.many2one('crm.case.channel','Distribution Chanel',required = True),
        'sale_tax':fields.many2one('account.tax','Sales Tax',required = True),
        'excise_duty':fields.char('Excise Duty',size = 1024),
    }
#     def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
#         vals = {}
#         if blanket_id:
#             emp = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
#             vals = {'customer_id':emp.customer_id.name,
#                     'avoice_add':emp.invoice_address,
#                     'payment_term_id':emp.payment_term_id.id,
#                     'po_date':emp.po_date,
# #                     'order_type':emp.
#                     'po_number':emp.po_number,
#                     'currency_id':emp.currency_id.id,
#                     'quotaion_no':emp.quotaion_no,
# #                     'incoterms_id':emp.currency_id.id,
#                     'distribution_chanel':emp.po_number,
#                     'currency_id':emp.currency_id.id,
#                     'quotaion_no':emp.quotaion_no,
#                     }
#         return {'value': vals}    

sale_order()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
