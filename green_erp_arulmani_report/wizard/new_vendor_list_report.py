# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class new_vendor_list_wizard(osv.osv_memory):
    _name = "new.vendor.list.wizard"
    
    _columns = {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('new.vendor.list.screen')
        
        this = self.browse(cr, uid, ids[0])
        screen_line = []
        name = ''
#         sql = '''
#             select rp.name as supplier_name, pt.name as material, po.notes as remark
#             from
#                 purchase_order_line pol
#                 left join purchase_order po on pol.order_id=po.id
#                 left join res_partner rp on po.partner_id=rp.id
#                 left join product_product pp on pol.product_id=pp.id
#                 left join product_template pt on pp.product_tmpl_id=pt.id
#             where po.state is not null 
#         '''
#         if this.date_from:
#             sql += '''
#                 and date(timezone('UTC',rp.create_date))>='%s'
#             '''%(this.date_from)
#         if this.date_to:
#             sql += '''
#                 and date(timezone('UTC',rp.create_date))<='%s'
#             '''%(this.date_to)
#             name = datetime.strptime(this.date_to,'%Y-%m-%d').strftime('%B %Y').upper()
#         sql += '''
#             group by rp.name, pt.name, po.notes
#         '''
        sql = '''
            select rp.id as partner_id, rp.name as supplier_name, vg.name as remark
            from
                res_partner rp
                left join tpt_vendor_group vg on rp.vendor_group_id=vg.id
            where rp.name is not null 
        '''
        if this.date_from:
            sql += '''
                and date(timezone('UTC',rp.create_date))>='%s'
            '''%(this.date_from)
        if this.date_to:
            sql += '''
                and date(timezone('UTC',rp.create_date))<='%s'
            '''%(this.date_to)
            name = datetime.strptime(this.date_to,'%Y-%m-%d').strftime('%B %Y').upper()
        cr.execute(sql)
        res = cr.dictfetchall()
        for seq,line in enumerate(res):
            material = ''
            sql = '''
                select pt.name as material
                from
                    purchase_order_line pol
                    left join purchase_order po on pol.order_id=po.id
                    left join res_partner rp on po.partner_id=rp.id
                    left join product_product pp on pol.product_id=pp.id
                    left join product_template pt on pp.product_tmpl_id=pt.id
                where po.partner_id=%s  group by pt.name limit 2
            '''%(line['partner_id'])
            cr.execute(sql)
            for product in cr.fetchall():
                material += (product and product[0] or '')+', '
            if material:
                material = material[:-2]
            line_vals = {
                'sequence': seq+1,
                'supplier_name': line['supplier_name'],
                'material': material,
                'remark': line['remark'],
            }
            screen_line.append((0,0,line_vals))
        vals = {
            'name': name,
            'screen_line': screen_line,
        }
        
        report_id = report_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_report', 'view_new_vendor_list_screen')
        return {
            'name': 'Monthwise LOP Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'new.vendor.list.screen',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': res and res[1] or False,
            'res_id': report_id,
        }
        
new_vendor_list_wizard()

class new_vendor_list_screen(osv.osv_memory):
    _name = "new.vendor.list.screen"
    
    _columns = {
        'name': fields.char('Name', size=1024),
        'screen_line': fields.one2many('new.vendor.list.screen.line', 'screen_id', 'Line'),
    }
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'new.vendor.list.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'new_vendor_list_report_xls', 'datas': datas}
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'new.vendor.list.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'new_vendor_list_report_pdf', 'datas': datas}
        
new_vendor_list_screen()

class new_vendor_list_screen_line(osv.osv_memory):
    _name = "new.vendor.list.screen.line"
    
    _columns = {
        'screen_id': fields.many2one('new.vendor.list.screen', 'Screen', ondelete='cascade'),
        'sequence': fields.integer('S.No'),
        'supplier_name': fields.char('Supplier name', size=1024),
        'material': fields.char('Material', size=1024),
        'remark': fields.char('Remarks', size=1024),
    }
        
new_vendor_list_screen_line()
