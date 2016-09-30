# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class single_source_vendor_wizard(osv.osv_memory):
    _name = "single.source.vendor.wizard"
    
    _columns = {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'po_document_type':fields.selection([('raw','VV Raw material PO'),('asset','VV Capital PO'),('standard','VV Standard PO'),
                                             ('local','VV Local PO'),('return','VV Return PO'),
                                             ('service','VV Service PO(Project)'),
                                             ('service_qty','VV Service PO(Qty Based)'),('service_amt','VV Service PO(Amt Based)'),
                                             ('out','VV Out Service PO')],'PO Document Type'),
        'rfq_category': fields.selection([('single','Single'),('special','Special')],'RFQ Type'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('single.source.vendor.screen')
        
        this = self.browse(cr, uid, ids[0])
        screen_line = []
        name = ''
        sql = '''
            select rp.name as supplier_name, pp.default_code as material_code, pt.name as material_name, pp.description as description,
                rfql.item_text as item_text, po.notes as remark
            from
                purchase_order_line pol
                left join purchase_order po on pol.order_id=po.id
                left join tpt_purchase_quotation pq on po.quotation_no=pq.id
                left join tpt_request_for_quotation rfq on pq.rfq_no_id=rfq.id
                left join tpt_rfq_line rfql on rfql.rfq_id=rfq.id and rfql.po_indent_id=pol.po_indent_no and rfql.product_id=pol.product_id
                left join res_partner rp on po.partner_id=rp.id
                left join product_product pp on pol.product_id=pp.id
                left join product_template pt on pp.product_tmpl_id=pt.id
            where po.state!='cancel' 
        '''
        if this.date_from:
            sql += '''
                and po.date_order>='%s'
            '''%(this.date_from)
        if this.date_to:
            sql += '''
                and po.date_order<='%s'
            '''%(this.date_to)
            name = datetime.strptime(this.date_to,'%Y-%m-%d').strftime('%B %Y').upper()
        if this.po_document_type:
            sql += '''
                and po.po_document_type='%s'
            '''%(this.po_document_type)
        if this.rfq_category:
            sql += '''
                and rfq.rfq_category='%s'
            '''%(this.rfq_category)
        sql += '''
            group by rp.name, pp.default_code, pt.name, pp.description, rfql.item_text, po.notes
        '''
        cr.execute(sql)
        res = cr.dictfetchall()
        for seq,line in enumerate(res):
            line_vals = {
                'sequence': seq+1,
                'supplier_name': line['supplier_name'],
                'material_code': line['material_code'],
                'material_name': line['material_name'],
                'description': line['description'],
                'item_text': line['item_text'],
                'remark': line['remark'],
            }
            screen_line.append((0,0,line_vals))
        vals = {
            'name': name,
            'screen_line': screen_line,
        }
        
        report_id = report_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_report', 'view_single_source_vendor_screen')
        return {
            'name': 'Monthwise LOP Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'single.source.vendor.screen',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': res and res[1] or False,
            'res_id': report_id,
        }
        
single_source_vendor_wizard()

class single_source_vendor_screen(osv.osv_memory):
    _name = "single.source.vendor.screen"
    
    _columns = {
        'name': fields.char('Name', size=1024),
        'screen_line': fields.one2many('single.source.vendor.screen.line', 'screen_id', 'Line'),
    }
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'single.source.vendor.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'single_source_vendor_report_xls', 'datas': datas}
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'single.source.vendor.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'single_source_vendor_report_pdf', 'datas': datas}
        
single_source_vendor_screen()

class single_source_vendor_screen_line(osv.osv_memory):
    _name = "single.source.vendor.screen.line"
    
    _columns = {
        'screen_id': fields.many2one('single.source.vendor.screen', 'Screen', ondelete='cascade'),
        'sequence': fields.integer('S.No'),
        'supplier_name': fields.char('Supplier name', size=1024),
        'material_code': fields.char('Material Code', size=1024),
        'material_name': fields.char('Material Name', size=1024),
        'description': fields.char('Description', size=1024),
        'item_text': fields.char('Item Text', size=1024),
        'remark': fields.char('Remarks', size=1024),
    }
        
single_source_vendor_screen_line()
