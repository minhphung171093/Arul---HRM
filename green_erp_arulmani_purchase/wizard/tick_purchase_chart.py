# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class tick_purchase_chart(osv.osv_memory):
    _name = "tick.purchase.chart"
    _columns = {    
                'po_document_type':fields.selection([('asset','VV Asset PO'),
                                                     ('standard','VV Standard PO'),
                                                     ('local','VV Local PO'),
                                                     ('return','VV Return PO'),
                                                     ('service','VV Service PO'),
                                                     ('out','VV Out Service PO')],'PO Document Type'),
                'message': fields.text(string="Message ", readonly=True),    
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        q_id = context.get('active_id')
        
        {
         
        }
tick_purchase_chart()