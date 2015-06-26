# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_batch_wise_stock(osv.osv_memory):
    _name = "tpt.batch.wise.stock"
    
    _columns = {    
        'batch_wise_line':fields.one2many('tpt.batch.wise.stock.line','batch_wise_id','Batch Wise Line'),
        'date': fields.date('Date'),
        'location_name': fields.char('Location Name', size=1024),
        'product_id':fields.many2one('product.product','Product Code'),
        'location_id':fields.many2one('stock.location','Warehouse Location'),
        'application_id':fields.many2one('crm.application','Application'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.batch.wise.stock'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.batch.wise.stock'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report_pdf', 'datas': datas}
    
tpt_batch_wise_stock()

class tpt_batch_wise_stock_line(osv.osv_memory):
    _name = "tpt.batch.wise.stock.line"
    
    _columns = {    
        'batch_wise_id':fields.many2one('tpt.batch.wise.stock','Batch Wise',ondelete='cascade'),
        'col_1': fields.char('',size=1024),
        'col_2': fields.char('',size=1024),
        'col_3': fields.char('',size=1024),
        'col_4': fields.char('',size=1024),
    }
    
tpt_batch_wise_stock_line()

class batch_wise_stock(osv.osv_memory):
    _name = "batch.wise.stock"
    _columns = {    
                'product_id':fields.many2one('product.product','Product Code'),
                'location_id':fields.many2one('stock.location','Warehouse Location',required=True),
                'application_id':fields.many2one('crm.application','Application'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'batch.wise.stock'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report', 'datas': datas}
        
        def get_line_product(o):
            product_data = o.product_id
            location_data = o.location_id
            if product_data:
                product_ids = [product_data.id]
            else:
                application_data = o.application_id
                if application_data:
                    sql = '''
                        select foo.product_id,case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_id,st.product_qty
                                from stock_move st 
                                where st.state='done' and st.location_dest_id = %s
                                    and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s )
                            union all
                            select st.product_id,st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.location_id = %s
                                    and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s )
                            )foo
                            group by foo.product_id
                    '''%(location_data.id,application_data.id,location_data.id,application_data.id)
                    cr.execute(sql)
                    product_ids = []
                    for r in cr.fetchall():
                        if r[1]>0:
                            product_ids.append(r[0])
                else:
                    sql = '''
                        select foo.product_id,case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_id,st.product_qty
                                from stock_move st 
                                where st.state='done' and st.location_dest_id = %s
                            union all
                            select st.product_id,st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.location_id = %s
                            )foo
                            group by foo.product_id
                    '''%(location_data.id,location_data.id)
                    cr.execute(sql)
                    product_ids = []
                    for r in cr.fetchall():
                        if r[1]>0:
                            product_ids.append(r[0])
            return self.pool.get('product.product').browse(cr, uid, product_ids)
        
        def get_line_batch(product,o):
            location_data = o.location_id
            application_data = o.application_id
            if application_data:
                sql = '''
                    select foo.prodlot_id,case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.prodlot_id,st.product_qty
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                        union all
                        select st.prodlot_id,st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_id = %s
                        )foo
                        where foo.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s )
                        group by foo.prodlot_id
                '''%(product.id,location_data.id,product.id,location_data.id,application_data.id)
                cr.execute(sql)
                tons = []
                for r in cr.fetchall():
                    if r[1]!=0:
                        tons.append(r)
            else: 
                sql = '''
                    select foo.prodlot_id,case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.prodlot_id,st.product_qty
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                        union all
                        select st.prodlot_id,st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_id = %s
                        )foo
                        group by foo.prodlot_id
                '''%(product.id,location_data.id,product.id,location_data.id)
                cr.execute(sql)
                tons = []
                for r in cr.fetchall():
                    if r[1]!=0:
                        tons.append(r)
            return tons
        
        def get_application(product,batch_id,o):
            def get_name_application(application_id=False):
                if application_id:
                    return self.pool.get('crm.application').browse(cr, uid, application_id).name
                else:
                    return ''
            application_data = o.application_id
            if application_data:
                return application_data.name
            else:
                if product and batch_id:
                    sql = 'select applicable_id from tpt_quality_verification where product_id = %s and prod_batch_id=%s'%(product.id,batch_id)
                    cr.execute(sql)
                    kq = cr.fetchone()
                    
                    return kq and get_name_application(kq[0]) or ''
                else:
                    return ''
        
        def get_batch_name(batch_id=False):
            if batch_id:
                return self.pool.get('stock.production.lot').browse(cr,uid,batch_id).name
            else:
                return 'Undefined'
            
        def get_total_qty(product,o):
            location_data = o.location_id
            application_data = o.application_id
            if application_data:
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.product_qty
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                                and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s )
                        union all
                        select st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_id = %s
                                and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s )
                        )foo
                '''%(product.id,location_data.id,application_data.id,product.id,location_data.id,application_data.id)
                cr.execute(sql)
                tons = cr.fetchone()[0]
            else: 
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.product_qty
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                        union all
                        select st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.product_id = %s and st.location_id = %s
                        )foo
                '''%(product.id,location_data.id,product.id,location_data.id)
                cr.execute(sql)
                tons = cr.fetchone()[0]
            return float(tons)
    
        cr.execute('delete from tpt_batch_wise_stock')
        bw_obj = self.pool.get('tpt.batch.wise.stock')
        bw = self.browse(cr, uid, ids[0])
        bw_line = []
        for product in get_line_product(bw):
            bw_line.append((0,0,{
                'col_1': 'Product Code: ',
                'col_2': product.default_code,
                'col_3': 'Product Name: '+product.name,
                'col_4': 'Total Qty: '+"{0:.3f}".format(get_total_qty(product,bw),','),
            }))
            bw_line.append((0,0,{
                'col_1': 'S.No',
                'col_2': 'Batch No',
                'col_3': 'Application',
                'col_4': 'On Hand Qty',
            }))
            for seq, line in enumerate(get_line_batch(product,bw)):
                bw_line.append((0,0,{
                    'col_1': str(seq+1),
                    'col_2': get_batch_name(line[0]),
                    'col_3': get_application(product,line[0],bw),
                    'col_4': "{0:.3f}".format(line[1],','),
                }))
        vals = {
            'batch_wise_line': bw_line,
            'date': time.strftime('%Y-%m-%d'),
            'location_name': bw.location_id and bw.location_id.name or '',
            'product_id': bw.product_id and bw.product_id.id or False,
            'location_id': bw.location_id and bw.location_id.id or False,
            'application_id': bw.application_id and bw.application_id.id or False,
        }
        bw_id = bw_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr,uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_batch_wise_stock_form')
        return {
                    'name': 'Batch Wise Stock',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.batch.wise.stock',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': bw_id,
                }
        
batch_wise_stock()