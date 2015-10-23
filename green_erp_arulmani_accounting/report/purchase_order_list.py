# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields,osv
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
import random

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class purchase_order_list(osv.osv_memory):
    _name = "purchase.order.list"
    _columns = {
        'si_no': fields.integer('SI.No', readonly=True),
        'po_id': fields.many2one('purchase.order','PO No', readonly=True),
        'po_date': fields.date('PO Date', readonly=True),
        'po_release_date': fields.date('PO Release Date', readonly=True),
        'supplier_id': fields.many2one('res.partner','Supplier Name', readonly=True),
        'line_no': fields.integer('Line No', readonly=True),
        'product_id': fields.many2one('product.product','Material Code', readonly=True),
        'material_name': fields.text('Material Name', readonly=True),
        'department_id': fields.many2one('hr.department','Department', readonly=True),
        'uom_id': fields.many2one('product.uom','UOM', readonly=True),
        'quantity': fields.float('Ordered Quantity',digits=(16,3), readonly=True),
        'unit_price': fields.float('Unit Price',digits=(16,2), readonly=True),
        'currency_id': fields.many2one('res.currency','UOM', readonly=True),
        'value': fields.float('Value',digits=(16,2), readonly=True),
        'pending_quantity': fields.float('Pending Quantity',digits=(16,3), readonly=True),
        'po_indent_no': fields.many2one('tpt.purchase.indent','Indent No', readonly=True),
        'indent_date': fields.date('Indent Date', readonly=True),
        'indent_release_date': fields.date('Indent Release Date', readonly=True),
    }

purchase_order_list()

#TPT- Y on 21/09/2015
class purchase_order_list_wizard(osv.osv_memory):
    _name = "purchase.order.list.wizard"
    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'po_no_from': fields.many2one('purchase.order','PO No From'),
        'po_no_to': fields.many2one('purchase.order','PO No To'),
        #'po_date_from': fields.date('PO Date From'),
        #'po_date_to': fields.date('PO Date To'),
        'sup_id': fields.many2one('res.partner','Supplier Name'),
        'prod_id': fields.many2one('product.product','Material Code'),
        'dept_id': fields.many2one('hr.department','Department'),
        'po_indent_no_from': fields.many2one('tpt.purchase.indent','Indent No From'),
        'po_indent_no_to': fields.many2one('tpt.purchase.indent','Indent No To'),
        'ind_date_from': fields.date('Indent Date From'),
        'ind_date_to': fields.date('Indent Date To'),
        'indent_release_date_from': fields.date('Indent Release Date From'),
        'indent_release_date_to': fields.date('Indent Release Date To'),
        'type_pend_qty':fields.selection([('with_zero', 'With Zero'),('without_zero', 'Without Zero')],'Pending Quantity'),
    }

    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    #Code changed by TPT-Y on 21Spet2015, for add more filtration      
    def view_report(self, cr, uid, ids, context=None):
        cr.execute('delete from purchase_order_list')
        purchase_order_list_obj = self.pool.get('purchase.order.list')
        order_line_obj = self.pool.get('purchase.order.line')
        line = self.browse(cr, uid, ids[0])
        date_from = line.date_from
        date_to = line.date_to
        
        po_no_from = ''
        po_no_to = ''
        po_indent_no_from = ''
        po_indent_no_to = ''
        
        purchase_order_obj = self.pool.get('purchase.order')        
        po_line_obj_from_ids = purchase_order_obj.search(cr, uid, [('id','=',line.po_no_from.id)])
        if po_line_obj_from_ids:
            po_no_name_from = purchase_order_obj.browse(cr,uid,po_line_obj_from_ids[0]) 
            po_no_from = po_no_name_from.name
        
        po_line_obj_to_ids = purchase_order_obj.search(cr, uid, [('id','=',line.po_no_to.id)])
        if po_line_obj_to_ids:
            po_no_name_to = purchase_order_obj.browse(cr,uid,po_line_obj_to_ids[0])    
            po_no_to = po_no_name_to.name
        
        purchase_indent_obj = self.pool.get('tpt.purchase.indent')        
        po_indent_obj_from_ids = purchase_indent_obj.search(cr, uid, [('id','=',line.po_indent_no_from.id)])
        if po_indent_obj_from_ids:
            po_indent_no_from = purchase_indent_obj.browse(cr,uid,po_indent_obj_from_ids[0]) 
            po_indent_no_from = po_indent_no_from.name
        
        po_line_obj_to_ids = purchase_indent_obj.search(cr, uid, [('id','=',line.po_indent_no_to.id)])
        if po_line_obj_to_ids:
            po_indent_no_to = purchase_indent_obj.browse(cr,uid,po_line_obj_to_ids[0])  
            po_indent_no_to = po_indent_no_to.name     
        
        sup_id = line.sup_id.id
        prod_id = line.prod_id.id
        dept_id = line.dept_id.id
        
        ind_date_from = line.ind_date_from
        ind_date_to = line.ind_date_to
        indent_release_date_from = line.indent_release_date_from
        indent_release_date_to = line.indent_release_date_to
        type_pend_qty = line.type_pend_qty
        
        if not date_from and not date_to and not po_no_from and not po_no_to and not po_indent_no_from and not po_indent_no_to and not sup_id and not prod_id and not dept_id and not ind_date_from and not ind_date_to and not indent_release_date_from and not indent_release_date_to and not type_pend_qty:
            raise osv.except_osv(_('Warning!'),_('Please Choose any one of Parameter'))
        
        
        #=======================================================================
        # sql = '''
        #     select id from purchase_order_line where order_id in (select id from purchase_order where date_order between '%s' and '%s')
        # '''%(date_from,date_to)
        #=======================================================================
        
        sql = '''
            select distinct pol.id as id
            from purchase_order_line pol
            join purchase_order po on (po.id = pol.order_id)
            join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
            join tpt_purchase_product pp on (pp.pur_product_id = pi.id and pol.product_id = pp.product_id)            
            '''
        
        if date_from or date_to or po_no_from or po_no_to or po_indent_no_from or po_indent_no_to or sup_id or prod_id or dept_id or ind_date_from or ind_date_to or indent_release_date_from or indent_release_date_to or type_pend_qty:
                    str = " where "
                    sql = sql+str
        if date_from and not date_to:
                    str = " po.date_order <= '%s'"%(date_from)
                    sql = sql+str               
        if date_to and not date_from:
                    str = " po.date_order >= '%s'"%(date_to)
                    sql = sql+str
        if date_to and date_from:
                    str = " po.date_order between '%s' and '%s'"%(date_from,date_to)
                    sql = sql+str                    
        if po_no_from and not po_no_to and not date_to and not date_from:
                    str = " po.name <= '%s'"%(po_no_from)
                    sql = sql+str                    
        if po_no_from and not po_no_to and (date_to or date_from):
                    str = " and po.name <= '%s'"%(po_no_from)
                    sql = sql+str                    
        if po_no_to and not po_no_from and not date_to and not date_from:
                    str = " po.name >= '%s' "%(po_no_to)
                    sql = sql+str                    
        if po_no_to and not po_no_from and (date_to or date_from):
                    str = " and po.name >= '%s' "%(po_no_to)
                    sql = sql+str
        if po_no_to and po_no_from and not date_to and not date_from:
                    str = " po.name between '%s' and '%s'"%(po_no_from,po_no_to)
                    sql = sql+str
        if po_no_to and po_no_from and (date_to or date_from):
                    str = " and po.name between '%s' and '%s'"%(po_no_from,po_no_to)
                    sql = sql+str             
        if sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.partner_id = %s"%(sup_id)
                    sql = sql+str       
        if sup_id and (po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.partner_id = %s"%(sup_id)
                    sql = sql+str                    
        if prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_id = %s"%(prod_id)
                    sql = sql+str  
        if prod_id and (sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_id = %s"%(prod_id)
                    sql = sql+str        
        if dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.department_id = %s"%(dept_id)
                    sql = sql+str  
        if dept_id and (prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.department_id = %s"%(dept_id)
                    sql = sql+str        
        if po_indent_no_from and not po_indent_no_to and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name <= '%s'"%(po_indent_no_from)
                    sql = sql+str  
        if po_indent_no_from and not po_indent_no_to and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name <= '%s'"%(po_indent_no_from)
                    sql = sql+str                    
        if po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name >= '%s'"%(po_indent_no_to)
                    sql = sql+str  
        if po_indent_no_to and not po_indent_no_from and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name >= '%s'"%(po_indent_no_to)
                    sql = sql+str
        if po_indent_no_to and po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name between '%s' and '%s'"%(po_indent_no_from,po_indent_no_to)
                    sql = sql+str  
        if po_indent_no_to and po_indent_no_from and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name between '%s' and '%s'"%(po_indent_no_from,po_indent_no_to)
                    sql = sql+str
        if ind_date_from and not ind_date_to and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent <= '%s'"%(ind_date_from)
                    sql = sql+str  
        if ind_date_from and not ind_date_to and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent <= '%s'"%(ind_date_from)
                    sql = sql+str
        if ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent <= '%s'"%(ind_date_to)
                    sql = sql+str  
        if ind_date_to and not ind_date_from and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent <= '%s'"%(ind_date_to)
                    sql = sql+str
        if ind_date_to and ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent between '%s' and '%s'"%(ind_date_from,ind_date_to)
                    sql = sql+str  
        if ind_date_to and ind_date_from and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent between '%s' and '%s'"%(ind_date_from,ind_date_to)
                    sql = sql+str
        if indent_release_date_from and not indent_release_date_to and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= %s"%(indent_release_date_from)
                    sql = sql+str
        if indent_release_date_from and not indent_release_date_to and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= %s"%(indent_release_date_from)
                    sql = sql+str                    
        if indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= %s"%(indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and not indent_release_date_from and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= %s"%(indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') between '%s' and '%s'"%(indent_release_date_from,indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and indent_release_date_from and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') between '%s' and '%s'"%(indent_release_date_from,indent_release_date_to)
                    sql = sql+str                    
        if type_pend_qty == 'with_zero' and not indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') = '0.00'"
                    sql = sql+str                    
        if type_pend_qty == 'with_zero' and (indent_release_date_to or indent_release_date_from or ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') = '0.00'"
                    sql = sql+str
        if type_pend_qty == 'without_zero' and not indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') <> '0.00'"
                    sql = sql+str                    
        if type_pend_qty == 'without_zero' and (indent_release_date_to or indent_release_date_from or ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') <> '0.00'"
                    sql = sql+str
         
        sql=sql+" order by id"       
                 
          
        
        cr.execute(sql)
        order_line_ids = [r[0] for r in cr.fetchall()]
        for seq,order_line in enumerate(order_line_obj.browse(cr, uid, order_line_ids)):
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                    from stock_move where purchase_line_id=%s and state='done'
                    and origin is not null
            '''%(order_line.id)
            cr.execute(sql)
            grn_qty = cr.fetchone()[0]
            
            ##    
            indent_line_obj = self.pool.get('tpt.purchase.product') 
            indent_line_obj_ids = indent_line_obj.search(cr, uid, [('pur_product_id','=',order_line.po_indent_no.id)])
            indent_line_obj1 = indent_line_obj.browse(cr,uid,indent_line_obj_ids[0])
            hod_date = indent_line_obj1.hod_date   
            ##
            vals = {
                'si_no': seq+1,
                'po_id': order_line.order_id.id,
                'po_date': order_line.order_id.date_order,
                'po_release_date': order_line.order_id.md_approve_date,
                'supplier_id': order_line.partner_id.id,
                'line_no': order_line.line_no,
                'product_id': order_line.product_id.id,
                'material_name': order_line.name,
                'department_id': order_line.po_indent_no.department_id and order_line.po_indent_no.department_id.id or False,
                'uom_id': order_line.product_uom.id,
                'quantity': order_line.product_qty,
                'unit_price': order_line.price_unit,
                'currency_id': order_line.order_id.currency_id.id,
                'value': order_line.product_qty*order_line.price_unit,
                'pending_quantity': order_line.product_qty-grn_qty,
                'po_indent_no': order_line.po_indent_no.id,
                'indent_date': order_line.po_indent_no.date_indent,
                'indent_release_date': hod_date or False,
            }
            purchase_order_list_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_purchase_order_list_tree')
        return {
                    'name': 'Purchase Order List',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'purchase.order.list',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'purchase.order.list.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'po_list_report', 'datas': datas}
    
purchase_order_list_wizard()

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({

            'view_report_xls':self.view_report_xls,
            'convert_date_cash':self.convert_date_cash,
            
        })
    
    def convert_date_cash(self,date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
            
            
    def view_report_xls(self):
        self.cr.execute('delete from purchase_order_list')
        purchase_order_list_obj = self.pool.get('purchase.order.list')
        order_line_obj = self.pool.get('purchase.order.line')
        vals = []
        #wizard_obj = self.pool.get('purchase.order.list.wizard')
        wizard_data = self.localcontext['data']['form']
        #date_from=wizard_data['date_from']        
        #line = wizard_obj.browse(self.cr, self.uid, ids[0])        
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        
        po_no_from = ''
        po_no_to = ''
        po_indent_no_from = ''
        po_indent_no_to = ''
        
        if wizard_data['po_no_from']:
            po_no_from = wizard_data['po_no_from'][1]
        if wizard_data['po_no_to']:
            po_no_to = wizard_data['po_no_to'][1]        
        sup_id = wizard_data['sup_id']
        prod_id = wizard_data['prod_id']
        dept_id = wizard_data['dept_id']
        
        if wizard_data['po_indent_no_from']:
            po_indent_no_from = wizard_data['po_indent_no_from'][1]
        if wizard_data['po_indent_no_to']:
            po_indent_no_to = wizard_data['po_indent_no_to'][1]
            
        ind_date_from = wizard_data['ind_date_from']
        ind_date_to = wizard_data['ind_date_to']
        indent_release_date_from = wizard_data['indent_release_date_from']
        indent_release_date_to = wizard_data['indent_release_date_to']
        type_pend_qty = wizard_data['type_pend_qty']
        
        
        if not date_from and not date_to and not po_no_from and not po_no_to and not po_indent_no_from and not po_indent_no_to and not sup_id and not prod_id and not dept_id and not ind_date_from and not ind_date_to and not indent_release_date_from and not indent_release_date_to and not type_pend_qty:
            raise osv.except_osv(_('Warning!'),_('Please Choose any one of Parameter'))
        
        
        #=======================================================================
        # sql = '''
        #     select id from purchase_order_line where order_id in (select id from purchase_order where date_order between '%s' and '%s')
        # '''%(date_from,date_to)
        #=======================================================================
        
        sql = '''
            select distinct pol.id as id
            from purchase_order_line pol
            join purchase_order po on (po.id = pol.order_id)
            join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
            join tpt_purchase_product pp on (pp.pur_product_id = pi.id and pol.product_id = pp.product_id)
             '''
        
        if date_from or date_to or po_no_from or po_no_to or po_indent_no_from or po_indent_no_to or sup_id or prod_id or dept_id or ind_date_from or ind_date_to or indent_release_date_from or indent_release_date_to or type_pend_qty:
                    str = " where "
                    sql = sql+str
        if date_from and not date_to:
                    str = " po.date_order <= '%s'"%(date_from)
                    sql = sql+str               
        if date_to and not date_from:
                    str = " po.date_order >= '%s'"%(date_to)
                    sql = sql+str
        if date_to and date_from:
                    str = " po.date_order between '%s' and '%s'"%(date_from,date_to)
                    sql = sql+str                    
        if po_no_from and not po_no_to and not date_to and not date_from:
                    str = " po.name <= '%s'"%(po_no_from)
                    sql = sql+str                    
        if po_no_from and not po_no_to and (date_to or date_from):
                    str = " and po.name <= '%s'"%(po_no_from)
                    sql = sql+str                    
        if po_no_to and not po_no_from and not date_to and not date_from:
                    str = " po.name >= '%s' "%(po_no_to)
                    sql = sql+str                    
        if po_no_to and not po_no_from and (date_to or date_from):
                    str = " and po.name >= '%s' "%(po_no_to)
                    sql = sql+str
        if po_no_to and po_no_from and not date_to and not date_from:
                    str = " po.name between '%s' and '%s'"%(po_no_from,po_no_to)
                    sql = sql+str
        if po_no_to and po_no_from and (date_to or date_from):
                    str = " and po.name between '%s' and '%s'"%(po_no_from,po_no_to)
                    sql = sql+str             
        if sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.partner_id = %s"%(sup_id[0])
                    sql = sql+str       
        if sup_id and (po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.partner_id = %s"%(sup_id[0])
                    sql = sql+str                    
        if prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_id = %s"%(prod_id[0])
                    sql = sql+str  
        if prod_id and (sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_id = %s"%(prod_id[0])
                    sql = sql+str        
        if dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.department_id = %s"%(dept_id[0])
                    sql = sql+str  
        if dept_id and (prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.department_id = %s"%(dept_id[0])
                    sql = sql+str        
        if po_indent_no_from and not po_indent_no_to and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name <= '%s'"%(po_indent_no_from)
                    sql = sql+str  
        if po_indent_no_from and not po_indent_no_to and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name <= '%s'"%(po_indent_no_from)
                    sql = sql+str                    
        if po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name >= '%s'"%(po_indent_no_to)
                    sql = sql+str  
        if po_indent_no_to and not po_indent_no_from and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name >= '%s'"%(po_indent_no_to)
                    sql = sql+str
        if po_indent_no_to and po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.name between '%s' and '%s'"%(po_indent_no_from,po_indent_no_to)
                    sql = sql+str  
        if po_indent_no_to and po_indent_no_from and (dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.name between '%s' and '%s'"%(po_indent_no_from,po_indent_no_to)
                    sql = sql+str
        if ind_date_from and not ind_date_to and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent <= '%s'"%(ind_date_from)
                    sql = sql+str  
        if ind_date_from and not ind_date_to and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent <= '%s'"%(ind_date_from)
                    sql = sql+str
        if ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent <= '%s'"%(ind_date_to)
                    sql = sql+str  
        if ind_date_to and not ind_date_from and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent <= '%s'"%(ind_date_to)
                    sql = sql+str
        if ind_date_to and ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pi.date_indent between '%s' and '%s'"%(ind_date_from,ind_date_to)
                    sql = sql+str  
        if ind_date_to and ind_date_from and (po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pi.date_indent between '%s' and '%s'"%(ind_date_from,ind_date_to)
                    sql = sql+str
        if indent_release_date_from and not indent_release_date_to and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= %s"%(indent_release_date_from)
                    sql = sql+str
        if indent_release_date_from and not indent_release_date_to and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') <= %s"%(indent_release_date_from)
                    sql = sql+str                    
        if indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= %s"%(indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and not indent_release_date_from and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') >= %s"%(indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') between '%s' and '%s'"%(indent_release_date_from,indent_release_date_to)
                    sql = sql+str
        if indent_release_date_to and indent_release_date_from and (ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and to_date(to_char(pp.hod_date, 'YYYY/MM/DD'), 'YYYY/MM/DD') between '%s' and '%s'"%(indent_release_date_from,indent_release_date_to)
                    sql = sql+str                    
        if type_pend_qty == 'with_zero' and not indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') = '0.00'"
                    sql = sql+str                    
        if type_pend_qty == 'with_zero' and (indent_release_date_to or indent_release_date_from or ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') = '0.00'"
                    sql = sql+str
        if type_pend_qty == 'without_zero' and not indent_release_date_to and not indent_release_date_from and not ind_date_to and not ind_date_from and not po_indent_no_to and not po_indent_no_from and not dept_id and not prod_id and not sup_id and not po_no_to and not po_no_from and not date_to and not date_from:
                    str = " pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') <> '0.00'"
                    sql = sql+str                    
        if type_pend_qty == 'without_zero' and (indent_release_date_to or indent_release_date_from or ind_date_to or ind_date_from or po_indent_no_to or po_indent_no_from or dept_id or prod_id or sup_id or po_no_to or po_no_from or date_to or date_from):
                    str = " and pol.product_qty - (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id=pol.id and state='done') <> '0.00'"
                    sql = sql+str

        sql=sql+" order by id"
                    
        
        self.cr.execute(sql)
        order_line_ids = [r[0] for r in self.cr.fetchall()]
        for seq,order_line in enumerate(order_line_obj.browse(self.cr, self.uid, order_line_ids)):
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                    from stock_move where purchase_line_id=%s and state='done'
                    and origin is not null
            '''%(order_line.id)
            self.cr.execute(sql)
            grn_qty = self.cr.fetchone()[0]
            
            ##    
            indent_line_obj = self.pool.get('tpt.purchase.product') 
            indent_line_obj_ids = indent_line_obj.search(self.cr, self.uid, [('pur_product_id','=',order_line.po_indent_no.id)])
            indent_line_obj1 = indent_line_obj.browse(self.cr,self.uid,indent_line_obj_ids[0])
            hod_date = indent_line_obj1.hod_date   
            ##
            vals.append ( {
                'si_no': seq+1,
                'po_id': order_line.order_id.name,
                'po_date': order_line.order_id.date_order,
                'po_release_date': order_line.order_id.md_approve_date,
                'supplier_id': order_line.partner_id.name,
                'line_no': order_line.line_no,
                'product_id': order_line.product_id.code +"-" + order_line.product_id.name,
                'material_name': order_line.name,
                'department_id': order_line.po_indent_no.department_id and order_line.po_indent_no.department_id.name or False,
                'uom_id': order_line.product_uom.name,
                'quantity': order_line.product_qty,
                'unit_price': order_line.price_unit,
                'currency_id': order_line.order_id.currency_id.name,
                'value': order_line.product_qty*order_line.price_unit,
                'pending_quantity': order_line.product_qty-grn_qty,
                'po_indent_no': order_line.po_indent_no.name,
                'indent_date': order_line.po_indent_no.date_indent,
                'indent_release_date': hod_date or False,
            })
        return vals
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: