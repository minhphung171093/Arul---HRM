# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_pr_history_report(osv.osv_memory):
    _name = "tpt.pr.history.report"
    _columns = {
             'name': fields.char('', readonly=True), 
             'ind_id':fields.many2one('tpt.purchase.indent', 'Indent Number'),                     
             #'date_from':fields.date('Date From'),
             #'date_to':fields.date('Date To'),             
             'pr_hist_line_id': fields.one2many('tpt.pr.history.line.report', 'pr_hist_id', 'PR History Line'),
    }
     
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.pr.history.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        #datas['form'].update({'active_id':context.get('active_ids',False)})
        datas['form'].update({'active_id':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_pr_history_report_pdf', 'datas': datas}
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.pr.history.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        #datas['form'].update({'active_id':context.get('active_ids',False)})
        datas['form'].update({'active_id':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_pr_history_report_xls', 'datas': datas}   
     
tpt_pr_history_report()

class tpt_pr_history_line_report(osv.osv_memory):
    _name = "tpt.pr.history.line.report"
     
    _columns = {
        'pr_hist_id': fields.many2one('tpt.pr.history.report','PR History', ondelete='cascade'),
        'pr_req_no' : fields.char('PR No'),
        'pr_date': fields.date('PR Date'),
        'pr_rel_date' : fields.date('PR Rel.by HOD'),
        'mat_code' : fields.char('Material Code'),
        'mat_name' : fields.char('Material Name'),
        'pr_qty' : fields.float('PR Qty',digits=(16,3)),
        'uom' : fields.char('UOM'),
        'rfq_date' : fields.date('RFQ Date'),
        'rfq_no' : fields.char('RFQ No'),
        'rfq_qty' : fields.float('PR Qty',digits=(16,3)),
        'po_date' : fields.date('PO Date'),
        'po_no' : fields.char('PO No'),
        'ven_name' : fields.char('Vendor Name'),
        'po_qty' : fields.float('PO Qty',digits=(16,3)),
        'po_hod_date' : fields.date('PO Rel.by HOD'),
        'po_md_date' : fields.date('PO Rel.by MD'),
        'grn_date' : fields.date('GRN Date'),
        'grn_no' : fields.char('GRN No'),
        'grn_qty' : fields.float('GRN Qty',digits=(16,3)),
        'inv_date' : fields.date('Invoice Date'),
        'inv_no' : fields.char('Invoice No'),
        'inv_tot_amt' : fields.float('Invoice Total Amount',digits=(16,3)),
        #'pr_req_no' : fields.char('PR No'),
        
        
 }
tpt_pr_history_line_report()


class pr_history_report(osv.osv_memory):
     _name = "pr.history.report"
     
     _columns = {
             #'date_from':fields.date('Date From'),
             #'date_to':fields.date('Date To'),
             'ind_id':fields.many2one('tpt.purchase.indent', 'Indent Number'),
                  
     }
 
    
     def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
     constraints = [
        (_check_date, 'Identical Data', []),
     ]
     
     
     def print_report(self, cr, uid, ids, context=None):
         
          
            def get_invoice(cb):
                res = {}
                ind_id = cb.ind_id.name        
                #date_from = cb.date_from
                #date_to = cb.date_to
                         
                sql = '''
                    select distinct tpi.date_indent as indentdate,tpi.name as indent_no,pp.name_template as mat_name,pp.default_code as mat_code,
                    tpp.hod_date as hodreldate,tpp.product_uom_qty as indentqty,pu.name as uom,rfql.product_uom_qty as rfqquantity,
                    rfq.rfq_date as rfqdate,rfq.name as rfqname,pol.product_qty as poqty,po.name as purchaseorderno,
                    po.date_order as podate,po.md_approve_date as mdapproveddate,rp.name as vendor,sm.product_qty as grnqty,
                    sp.name as grnno,sp.date as grndate,ai.name as invoiceno,ai.date_invoice as invoicedate,ai.amount_total as invoicetotal                    
                    from tpt_purchase_indent as tpi
                    inner join tpt_purchase_product as tpp on tpi.id = tpp.pur_product_id
                    join product_product pp on pp.id = tpp.product_id
                    inner join product_uom as pu on tpp.uom_po_id=pu.id
                    left join tpt_rfq_line as rfql on tpp.id = rfql.indent_line_id
                    left join tpt_request_for_quotation as rfq on rfql.rfq_id=rfq.id
                    left join purchase_order_line as pol on tpp.pur_product_id=pol.po_indent_no and tpp.description = pol.description
                    left join purchase_order as po on pol.order_id=po.id
                    left join res_partner as rp on po.partner_id=rp.id
                    left join stock_move as sm on tpp.pur_product_id=sm.po_indent_id and tpp.description=sm.description
                    left join stock_picking as sp on sm.picking_id=sp.id and po.id=sp.purchase_id
                    left join account_invoice as ai on sm.picking_id=ai.grn_no
                    where tpi.name = '%s'
                    '''%(ind_id)
                                     
                cr.execute(sql)
                return cr.dictfetchall()
             
            cr.execute('delete from tpt_pr_history_report')
            cb_obj = self.pool.get('tpt.pr.history.report')
            cb = self.browse(cr, uid, ids[0])
            cb_line = []
            for line in get_invoice(cb):
                cb_line.append((0,0,{                             
                            'pr_req_no' : line['indent_no'] or '',
                            'pr_date': line['indentdate'] or False,
                            'pr_rel_date':line['hodreldate'] or False,
                            'mat_code':line['mat_code'] or '',
                            'mat_name':line['mat_name'] or '',
                            'pr_qty':line['indentqty'] or '',
                            'uom':line['uom'] or '',
                            'rfq_date':line['rfqdate'] or False,
                            'rfq_no':line['rfqname'] or '',
                            'rfq_qty':line['rfqquantity'] or '',
                            'po_date':line['podate'] or False,
                            'po_no':line['purchaseorderno'] or '',
                            'ven_name':line['vendor'] or '',
                            'po_qty':line['poqty'] or '',                            
                            'po_md_date':line['mdapproveddate'] or False,
                            'grn_date':line['grndate'] or False,
                            'grn_no':line['grnno'] or '',
                            'grn_qty':line['grnqty'] or '',
                            'inv_date':line['invoicedate'] or False,
                            'inv_no':line['invoiceno'] or '',
                            'inv_tot_amt':line['invoicetotal'] or '',        
                            
                }))
             
            vals = {
                'name': 'PR History Report',               
                'ind_id': cb.ind_id.name,
                #'date_to': cb.date_to,
                'pr_hist_line_id': cb_line,
            }
            cb_id = cb_obj.create(cr, uid, vals)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_purchase', 'view_tpt_pr_history_report')
            return {
                        'name': 'PR History Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.pr.history.report',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': cb_id,
                    }
         
         
         #======================================================================
         # if context is None:
         #     context = {}
         # datas = {'ids': context.get('active_ids', [])}
         # datas['model'] = 'pr.history.report'
         # datas['form'] = self.read(cr, uid, ids)[0]
         # datas['form'].update({'active_id':context.get('active_ids',False)})
         # return {'type': 'ir.actions.report.xml', 'report_name': 'material_request_line_report', 'datas': datas}
         #======================================================================
        

pr_history_report()