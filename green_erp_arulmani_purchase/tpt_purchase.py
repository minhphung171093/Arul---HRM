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
from openerp import netsvc

class tpt_mrp_process(osv.osv):
    _name = "tpt.mrp.process"
    _columns = {
        'name':fields.date('MRP Date',required = True,states={'done':[('readonly', True)]}),
        'mrp_process_line':fields.one2many('tpt.mrp.process.line','mrp_process_id','Vendor Group',states={'done':[('readonly', True)]}),
        'flag':fields.boolean('Flag'),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('approve', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'approve':[('readonly', True)]}),
                }
    _defaults={
               'state': 'draft',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'approve'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def bt_run_mrp(self, cr, uid, ids, context=None):
        mrp_process_line = []
        for mrp in self.browse(cr, uid, ids):
            sql = '''
                    delete from tpt_mrp_process_line
                    where mrp_process_id = %s
                '''%(mrp.id)
            cr.execute(sql)
        sql = '''
                select product_product.id, uom_po_id
                from product_product, product_template
                where mrp_control = True and max_stock >= re_stock and product_product.id = product_template.id
            '''
        cr.execute(sql)
        prod_ids = cr.dictfetchall()
        if prod_ids:
            for prod in prod_ids:
                mrp_process_line.append((0,0,{'product_id':prod['id'],
                                              'uom_po_id':prod['uom_po_id'],
                                              }))
        return self.write(cr,uid,ids,{'mrp_process_line':mrp_process_line})
    
    def bt_generate_indent(self, cr, uid, ids, context=None):
        purchase_product_line = []
        depa_id = False
        po_indent_obj = self.pool.get('tpt.purchase.indent')
        for mrp in self.browse(cr, uid, ids):
            if mrp.mrp_process_line:
                for line in mrp.mrp_process_line:
                    if line.select:
                        purchase_product_line.append((0,0,{'product_id':line.product_id.id,
                                                           'product_uom_qty':line.product_uom_qty or False,
                                                           'uom_po_id':line.uom_po_id and line.uom_po_id.id or False,
                                                           }))
            sql = '''
                select id from hr_department where name = 'PRODUCTION'
                '''
            cr.execute(sql)
            depa_ids = cr.fetchone()
            if depa_ids:
                depa_id = depa_ids[0] or False
                        
            po_indent_obj.create(cr, uid,{'document_type': 'base',
                                            'department_id': depa_id,
                                            'intdent_cate': 'normal',
                                            'purchase_product_line':purchase_product_line,
                                            'state': 'draft',
                                            }, context)
            sql = '''
                update tpt_mrp_process set flag = True
                '''
            cr.execute(sql)
        return True
tpt_mrp_process()


class tpt_mrp_process_line(osv.osv):
    _name = "tpt.mrp.process.line"
    _columns = {
        'product_id': fields.many2one('product.product','Material',required = True),
        'select':fields.boolean('Select'),
        'product_uom_qty': fields.float('Quantity'),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'mrp_process_id': fields.many2one('tpt.mrp.process', 'Material'),
                }
tpt_mrp_process_line()
