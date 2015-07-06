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
        no_ind_product_ids = []
        ind_product_ids = []
        mrp_product_ids = []
        product_obj = self.pool.get('product.product')
        for mrp in self.browse(cr, uid, ids):
            sql = '''
                    delete from tpt_mrp_process_line
                    where mrp_process_id = %s
                '''%(mrp.id)
            cr.execute(sql)
            sql = '''
                    select id
                    from product_product
                    where mrp_control = True and 
                            ((re_stock is not null and (select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
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
                            ) <= re_stock)
                            or
                            (re_stock is null and (select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
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
                            ) <= 0)
                            )
                '''
            cr.execute(sql)
            prod_ids = cr.fetchall()
            if prod_ids:
                product_ids = [r[0] for r in prod_ids]
#                 # nhung product da tao indent
#                 sql='''
#                     select product_id from tpt_purchase_indent,tpt_purchase_product 
#                     where tpt_purchase_indent.id = tpt_purchase_product.pur_product_id and tpt_purchase_indent.document_type = 'base'
#                         and tpt_purchase_indent.state != 'cancel'
#                 '''
#                 cr.execute(sql)
#                 product_ind_ids = cr.fetchall()
#                 if product_ind_ids:
#                     cr.execute('''
#                             select id from product_product where id in %s and id not in %s
#                         ''',(tuple(product_ids),tuple(product_ind_ids),))
#                     no_ind_product_ids = [r[0] for r in cr.fetchall()]
#                     # no_ind_product_ids danh sach cac san pham chua co indent
#                 sql='''
#                     select distinct(ind.id) from tpt_purchase_indent ind,tpt_purchase_product line
#                     where ind.id = line.pur_product_id and ind.document_type = 'base'
#                         and ind.state != 'cancel' and line.product_uom_qty = line.rfq_qty
#                 '''
#                 cr.execute(sql)
#                 full_ind_ids = cr.fetchall()
#                 #full_ind_ids danh sach indent da tao rfq toan phan
#                 sql = '''
#                      select distinct(po_indent_id) from stock_move sm, tpt_purchase_indent ind
#                      where sm.state != 'done' and po_indent_id is not NULL and ind.id = sm.po_indent_id and ind.document_type = 'base'
#                  '''
#                 cr.execute(sql)
#                 not_receive_ind_ids = cr.fetchall()
#                 #not_receive_ind_ids nhung indent co GRN nhung chua done
#                 if full_ind_ids and not_receive_ind_ids:
#                     cr.execute('''
#                             select distinct(id) from tpt_purchase_indent where id in %s and id not in %s
#                         ''',(tuple(full_ind_ids),tuple(not_receive_ind_ids),))
#                     indent_ids = [r[0] for r in cr.fetchall()] 
#                     if indent_ids:
#                         
#                         sql = '''
#                             select product_id from tpt_purchase_indent ind, tpt_purchase_product line
#                             where ind.id = line.pur_product_id and ind.id in %s and line.product_uom_qty = line.rfq_qty and product_id in %s
#                             and product_id in (select st.product_id from stock_move st, tpt_purchase_indent ind 
#                                                where st.po_indent_id = ind.id and ind.document_type = 'base' and st.state = 'done')
#                         '''%(tuple(indent_ids),tuple(product_ids))
#                         print sql
#                         cr.execute('''
#                             select product_id from tpt_purchase_indent ind, tpt_purchase_product line
#                             where ind.id = line.pur_product_id and ind.id in %s and line.product_uom_qty = line.rfq_qty and product_id in %s
#                             and product_id in (select st.product_id from stock_move st, tpt_purchase_indent ind 
#                                                 where st.po_indent_id = ind.id and ind.document_type = 'base' and st.state = 'done')
#                         ''',(tuple(indent_ids),tuple(product_ids),))
#                         ind_product_ids = [r[0] for r in cr.fetchall()] 
#                 if ind_product_ids and no_ind_product_ids:
#                     cr.execute('''
#                         select distinct(id) from product_product
#                         where id in %s or id in %s
#                     ''',(tuple(ind_product_ids),tuple(no_ind_product_ids),))
#                     mrp_product_ids = [r[0] for r in cr.fetchall()] 
#                 if ind_product_ids and not no_ind_product_ids:
#                     cr.execute('''
#                         select distinct(id) from product_product
#                         where id in %s
#                     ''',(tuple(ind_product_ids),))
#                     mrp_product_ids = [r[0] for r in cr.fetchall()] 
#                 if not ind_product_ids and no_ind_product_ids:
#                     cr.execute('''
#                         select distinct(id) from product_product
#                         where id in %s
#                     ''',(tuple(no_ind_product_ids),))
#                     mrp_product_ids = [r[0] for r in cr.fetchall()] 
                
                mrp_prod_ids=[]
                cr.execute('''
                    select distinct(product_id) from tpt_purchase_product where product_id in %s and 
                        pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel') 
                            and state in ('x','xx') and date_indent_relate = (select max(date_indent_relate) from tpt_purchase_product
                                            where pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel'))
                ''',(tuple(product_ids),))
                for line in cr.fetchall():
#                     sql = '''
#                         select distinct(product_id) from tpt_purchase_product 
#                         where pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel') 
#                         and date_indent_relate = (select max(date_indent_relate) from tpt_purchase_product
#                                             where pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel') ) 
#                     '''
#                     cr.execute(sql)
#                     max_prod_ids = [r[0] for r in cr.fetchall()]
#                     if line in max_prod_ids:
                    mrp_product_ids.append({'product_id':line[0],'indent_line_id':False})
                    mrp_prod_ids.append(line[0])
                        
#                 cr.execute('''
#                     select pur_product_id,product_id,id from tpt_purchase_product 
#                         where pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel')
#                             and product_id in %s and product_uom_qty = rfq_qty and is_mrp!='t' 
#                 ''',(tuple(product_ids),))

#                 bo di dk trong cau query product_uom_qty = rfq_qty va thay bang is not True
                cr.execute('''
                    select pur_product_id,product_id,id from tpt_purchase_product 
                        where pur_product_id in (select id from tpt_purchase_indent where document_type = 'base' and state != 'cancel')
                            and product_id in %s and is_mrp is not True
                ''',(tuple(product_ids),))
                indent_line_ids = []
                
                for line in cr.fetchall():
#                     sql = '''
#                         select id from tpt_purchase_product where product_id = %s and pur_product_id = %s and state in ('x','xx','close')
#                     '''%(line[1],line[0])
#                     cr.execute(sql)
#                     po_line_ids = [r[0] for r in cr.fetchall()]
#                     if po_line_ids:
#                         mrp_product_ids.append({'product_id':line[1],'indent_line_id':False})
                    sql = '''
                        select id from stock_move where po_indent_id=%s and product_id=%s
                    '''%(line[0],line[1])
                    cr.execute(sql)
                    move_ids = [r[0] for r in cr.fetchall()]
                    if move_ids:
                        cr.execute('''
                             select id from stock_move where id in %s and state not in ('done','cancel')
                        ''',(tuple(move_ids),))
                        m_ids = [r[0] for r in cr.fetchall()]
                        if not m_ids:
                            mrp_product_ids.append({'product_id':line[1],'indent_line_id':line[2]})
                            mrp_prod_ids.append(line[1])
#                             indent_line_ids.append(line[3])
                
                sql='''
                    select distinct(product_id) from tpt_purchase_indent,tpt_purchase_product 
                    where tpt_purchase_indent.id = tpt_purchase_product.pur_product_id and tpt_purchase_indent.document_type = 'base'
                        and tpt_purchase_indent.state != 'cancel'
                '''
                cr.execute(sql)
                product_ind_ids = cr.fetchall()
                if product_ind_ids:
                    cr.execute('''
                            select distinct(id) from product_product where id in %s and id not in %s
                        ''',(tuple(product_ids),tuple(product_ind_ids),))
                    for r in cr.fetchall():
                        if r[0] not in mrp_prod_ids:
                            mrp_product_ids.append({'product_id':r[0],'indent_line_id':False})
                
                if mrp_product_ids:
#                     cr.execute('''
#                         select id, max_stock, min_stock, re_stock from product_product
#                         where id in %s
#                     ''',(tuple(mrp_product_ids)),)
#                     product_ids = [r[0] for r in cr.fetchall()] 
                    
                    
                    for product in mrp_product_ids:
                        prod = product_obj.browse(cr, uid, product['product_id'])
                        quantity = 1.00
                        hand_quantity = 0
                        sql = '''
                            select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                                    (select st.product_qty
                                        from stock_move st 
                                            inner join stock_location l2 on st.location_dest_id= l2.id
                                            inner join product_uom pu on st.product_uom = pu.id
                                        where st.state='done' and st.product_id = %s and l2.usage = 'internal'
                                    union all
                                    select st.product_qty*-1
                                        from stock_move st 
                                            inner join stock_location l1 on st.location_id= l1.id
                                            inner join product_uom pu on st.product_uom = pu.id
                                        where st.state='done' and st.product_id = %s and l1.usage = 'internal'
                                    )foo
                        '''%(prod.id,prod.id)
                        cr.execute(sql)
                        out = cr.dictfetchone()
                        if out:
                            hand_quantity = hand_quantity+float(out['ton_sl'])
    #                     maximum = line.product_id.max_stock or 0.0
                        if prod.max_stock > 0:
                            quantity =  prod.max_stock - hand_quantity
                        mrp_process_line.append((0,0,{'product_id':prod.id,
                                                      'uom_po_id':prod.uom_po_id.id,
                                                      'product_uom_qty':quantity,
                                                      'min_stock': prod.min_stock,  
                                                      'max_stock': prod.max_stock,  
                                                      're_stock': prod.re_stock,
                                                      'indent_line_id': product['indent_line_id'],
                                                      }))
        vals = {'mrp_process_line':mrp_process_line, 'state':'approve'}
        return self.write(cr,1,ids,vals)
    
    def bt_generate_indent(self, cr, uid, ids, context=None):
        purchase_product_line = []
        depa_id = False
        section_id = False
        count = 0
        hand_quantity = 0
        po_indent_obj = self.pool.get('tpt.purchase.indent')
        for mrp in self.browse(cr, uid, ids):
            sql = '''
                select id from hr_department where name in ('Stores','STORES')
                '''
            cr.execute(sql)
            depa_ids = cr.fetchone()
            if depa_ids:
                depa_id = depa_ids[0] or False
                
                sql = '''
                    select id from arul_hr_section where name in ('Stores','STORES') and department_id = %s
                    '''%(depa_id)
                cr.execute(sql)
                section_ids = cr.fetchone()
                if section_ids:
                    section_id = section_ids[0] or False
                
            indent_id = po_indent_obj.create(cr, 1,{'document_type': 'base',
                                            'department_id': depa_id,
                                            'section_id': section_id,
                                            'intdent_cate': 'normal',
                                            'purchase_product_line':purchase_product_line,
                                            'state': 'draft',
                                            }, context)
            if mrp.mrp_process_line:
                for line in mrp.mrp_process_line:
                    if line.select:
                        count+=1
                        purchase_product_line.append((0,0,{'product_id':line.product_id.id,
#                                                            'product_uom_qty':quantity,
                                                            'product_uom_qty':line.product_uom_qty or False,
                                                           'uom_po_id':line.uom_po_id and line.uom_po_id.id or False,
                                                            'pur_product_id': indent_id or False,
                                                            'doc_type_relate': 'base',
                                                           }))
                        if line.indent_line_id:
                            cr.execute(''' update tpt_purchase_product set is_mrp='t' where id = %s ''',(line.indent_line_id.id,))
            else: count = 0
            
            if count == 0:
                raise osv.except_osv(_('Warning!'),_('Can not be generate indent without selected product'))
            po_indent_obj.write(cr, 1,indent_id,{
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
        'product_uom_qty': fields.float('Requested Qty',digits=(16,3)),   
        'min_stock': fields.float('Min. Qty',digits=(16,3)),  
        'max_stock': fields.float('Max. Qty',digits=(16,3)),  
        're_stock': fields.float('Reorder Level',digits=(16,3)),  
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'mrp_process_id': fields.many2one('tpt.mrp.process', 'Material'),
        'indent_line_id':fields.many2one('tpt.purchase.product','Indent Line'),
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
