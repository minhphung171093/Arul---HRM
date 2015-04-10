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
                    where mrp_control = True and  (
                            select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                                (select st.product_qty
                                    from stock_move st 
                                        inner join stock_location l2 on st.location_dest_id= l2.id
                                        inner join product_uom pu on st.product_uom = pu.id
                                    where st.state='done' and st.product_id=product_product.id and l2.usage = 'internal'
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                        inner join stock_location l1 on st.location_id= l1.id
                                        inner join product_uom pu on st.product_uom = pu.id
                                    where st.state='done' and st.product_id=product_product.id and l1.usage = 'internal'
                                )foo
                            ) <= re_stock and product_product.product_tmpl_id = product_template.id
                    and (product_product.id not in (select product_id from tpt_purchase_indent,tpt_purchase_product 
                            where tpt_purchase_indent.id = tpt_purchase_product.pur_product_id 
                            and tpt_purchase_indent.state != 'cancel')
                        or product_product.id in (select product_id from tpt_purchase_indent,tpt_purchase_product 
                            where tpt_purchase_indent.id = tpt_purchase_product.pur_product_id 
                            and tpt_purchase_indent.state != 'cancel' 
                            and tpt_purchase_indent.id in (select po_indent_id from stock_move
                            where state = 'done')))
                '''
            cr.execute(sql)
            prod_ids = cr.dictfetchall()
            if prod_ids:
                for prod in prod_ids:
                    mrp_process_line.append((0,0,{'product_id':prod['id'],
                                                  'uom_po_id':prod['uom_po_id'],
                                                  }))
        return self.write(cr,uid,ids,{'mrp_process_line':mrp_process_line, 'state':'approve'})
    
    def bt_generate_indent(self, cr, uid, ids, context=None):
        purchase_product_line = []
        depa_id = False
        count = 0
        po_indent_obj = self.pool.get('tpt.purchase.indent')
        for mrp in self.browse(cr, uid, ids):
            sql = '''
                select id from hr_department where name = 'PRODUCTION'
                '''
            cr.execute(sql)
            depa_ids = cr.fetchone()
            if depa_ids:
                depa_id = depa_ids[0] or False
                
            indent_id = po_indent_obj.create(cr, uid,{'document_type': 'base',
                                            'department_id': depa_id,
                                            'intdent_cate': 'normal',
                                            'purchase_product_line':purchase_product_line,
                                            'state': 'draft',
                                            }, context)
            if mrp.mrp_process_line:
                for line in mrp.mrp_process_line:
                    if line.select:
                        count+=1
                        purchase_product_line.append((0,0,{'product_id':line.product_id.id,
                                                           'product_uom_qty':line.product_uom_qty or False,
                                                           'uom_po_id':line.uom_po_id and line.uom_po_id.id or False,
                                                            'pur_product_id': indent_id or False,
                                                           }))
            else: count = 0
            
            if count == 0:
                raise osv.except_osv(_('Warning!'),_('Can not be generate indent without selected product'))
            po_indent_obj.write(cr, uid,indent_id,{
                                            'purchase_product_line':purchase_product_line,
                                            })
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
    _defaults={
               'product_uom_qty': 1.00,
    }
tpt_mrp_process_line()

class tpt_project(osv.osv):
    _name = 'tpt.project'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
        'code': fields.char('Code', size=1024, required = True),
        'description': fields.text('Description'),
        'project_section_line': fields.one2many('tpt.project.section', 'project_id', 'Product Section'),
        
    }
    
    def _check_code(self, cr, uid, ids, context=None):
        for department in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_project where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(department.id,department.code,department.name)
            cr.execute(sql)
            department_ids = [row[0] for row in cr.fetchall()]
            if department_ids: 
                raise osv.except_osv(_('Warning!'),_('This name or code is duplicated!')) 
                return False
        return True
    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ] 
    
tpt_project()

class tpt_project_section(osv.osv):
    _name = 'tpt.project.section'
    _columns = {
        'project_id': fields.many2one('tpt.project', 'Project',ondelete='cascade'),
        'name': fields.char('Name', size=1024, required = True),
        'code': fields.char('Code', size=1024, required = True),
    }
    
    def _check_code(self, cr, uid, ids, context=None):
        for department in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_project_section where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(department.id,department.code,department.name)
            cr.execute(sql)
            department_ids = [row[0] for row in cr.fetchall()]
            if department_ids:  
                raise osv.except_osv(_('Warning!'),_('This name or code is duplicated!'))
                return False
        return True
    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ] 
    
    
tpt_project_section()
