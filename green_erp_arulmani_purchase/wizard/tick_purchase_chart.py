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
                'po_document_type':fields.selection([('raw','VV Raw material PO'),
                                                     ('asset','VV Capital PO'),
                                                     ('standard','VV Standard PO'),
                                                     ('local','VV Local PO'),
                                                     ('return','VV Return PO'),
                                                     ('service','VV Service PO(Project)'),
                                                     ('service_qty','VV Service PO(Qty Based)'),
                                                     ('service_amt','VV Service PO(Amt Based)'),
                                                     ('out','VV Out Service PO')],'PO Document Type',required=True),
                'message': fields.text(string="Message ", readonly=True),    
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        purchase_order_obj = self.pool.get('purchase.order')
        q_id = context.get('active_id')
        chart = self.pool.get('tpt.purchase.quotation').browse(cr, uid, q_id)
        location_ids=self.pool.get('stock.warehouse').search(cr, uid,[('company_id','=',chart.supplier_id.company_id.id)])
        location = self.pool.get('stock.warehouse').browse(cr, uid, location_ids[0])
        
        tick = self.browse(cr, uid, ids[0])
        new_po_ids = []
        if not chart.currency_id:
            raise osv.except_osv(_('Warning!'),_('Currency is not null, please configure it in Quotation master !'))
        # Added by P.vinothkumar on 17/10/2016 for validate pan and tin no must be 10 digits
        pan_tin = chart.supplier_id.pan_tin
        tin = chart.supplier_id.tin
        tin = tin.replace(" ", "")
        pan = pan_tin.replace(" ", "")
        if pan == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the pan number!'))
        if len(chart.supplier_id.pan_tin) < 10:
            raise osv.except_osv(_('Warning!'),_('Please enter correct pan number'))
        if tin == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the tin number!'))
        if len(chart.supplier_id.tin) < 11:
            raise osv.except_osv(_('Warning!'),_('Please enter correct tin number'))
        for line in chart.purchase_quotation_line:
            if line.po_indent_id.document_type == 'local':
                if tick.po_document_type != 'local':
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))
            if line.po_indent_id.document_type == 'capital':
                if tick.po_document_type != 'asset':
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))
            if line.po_indent_id.document_type == 'raw':
                if tick.po_document_type != 'raw':
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))
            if line.po_indent_id.document_type == 'service':
                if tick.po_document_type not in ('service', 'service_qty', 'service_amt'):
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))            
            if line.po_indent_id.document_type == 'outside':
                if tick.po_document_type != 'out':
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))
            if line.po_indent_id.document_type in ('maintanance','spare','normal','base','consumable'):
                if tick.po_document_type != 'standard':
                    raise osv.except_osv(_('Warning!'),_('Indent not allowed create with this Document Type'))            
            purchase_line = [(0,0,{
                'po_indent_no':line.po_indent_id.id,
                'discount':line.disc,
                'p_f':line.p_f,
                'p_f_type':line.p_f_type,
                'ed':line.e_d,
                'ed_type':line.e_d_type,
                'fright':line.fright,
                'fright_type':line.fright_type,
                'taxes_id':[(6,0,[line.tax_id and line.tax_id.id])],
                'name':'/',
                'item_text': line.item_text or False,
                })]
        line_vals = purchase_order_obj.onchange_quotation_no(cr, uid, [],chart.id)['value']['order_line']
        vals = purchase_order_obj.onchange_partner_id(cr, uid, [],chart.supplier_id.id)['value']
        vals.update({
                    'po_document_type': tick.po_document_type,
                    'quotation_no':chart.id,
                    'partner_id':chart.supplier_id and chart.supplier_id.id,
                    'partner_ref':chart.quotation_ref,
                    'date_order':chart.date_quotation,
                    'state_id':chart.supplier_id.state_id and chart.supplier_id.state_id.id,
                    'invoice_method': 'picking',
                    #TPT START
                    'mode_dis': chart.mode_dis or False,
                    'freight_term': chart.freight_term or False,
                    #'quotation_ref': chart.quotation_ref or '',
                    'for_basis': chart.for_basis or False,
                    'deli_sche': chart.schedule or False,
                    'payment_term_id':chart.payment_term_id and chart.payment_term_id.id or False,  
                     #TPT END
                    
#                         'po_indent_no':line.po_indent_id.id,
                    'order_line': line_vals,
                    'currency_id':chart.currency_id and chart.currency_id.id or False,
                    'tpt_currency_id':chart.currency_id and chart.currency_id.id or False,
                    'location_id':location.lot_stock_id.id,
                    })
        new_po_id = purchase_order_obj.create(cr, uid, vals)
        new_po_ids.append(new_po_id)
        sql = '''
            update tpt_purchase_quotation set state = 'done', comparison_chart_id=null where id = %s
        '''%(chart.id)
        cr.execute(sql)
        
        
        
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'purchase', 'purchase_order_tree')
        return {
                    'name': 'Purchase Order',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'purchase.order',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': new_po_ids,
                    'domain': [('id', 'in', new_po_ids)],
                }
        
tick_purchase_chart()