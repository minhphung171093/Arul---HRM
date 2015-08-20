# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class tpt_general_ledger_from(osv.osv_memory):
    _name = "tpt.general.ledger.from"
    _columns = {
        'name': fields.char('', readonly=True),
        'account_id':fields.many2one('account.account','GL Account'),
        'date_from_title': fields.char('', size = 1024), #TPT-Y
        'date_to_title': fields.char('', size = 1024), #TPT-Y
        'gl_code_desc': fields.char('', size = 1024), #TPT-Y
        'gl_desc': fields.char('', size = 1024), #TPT-Y
        'emp_desc': fields.char('', size = 1024), #TPT-Y
        'doc_type': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Executives Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('ser_inv', 'Service Invoice'),
                                  ('product', 'Production'),
                                  ('staff_payroll', 'Staff Payroll'),
                                  ('worker_payroll', 'Workers Payroll')],'Document Type'),   
        'doc_no':fields.char('Document No',size=1024),
        'narration':fields.char('Narration',size=1024),
        'general_ledger_line': fields.one2many('tpt.general.ledger.line', 'ledger_id', 'General Line'),
        #'date_from': fields.date('Posting ate From', required=True),
        #'date_to': fields.date('To', required=True),
        #'is_posted': fields.boolean('Is Posted'),
        'date_from': fields.date('Posting Date From', required=True), #TPT-Y
        'date_to': fields.date('To', required=True), #TPT-Y
        'employee': fields.many2one('res.partner', 'Vendor/Customer',ondelete='restrict'),#TPT-Y
        'cost_center_id':fields.many2one('tpt.cost.center','Cost Center'),#TPT-Y   
        'is_posted': fields.boolean('Is Posted'),  #TPT-Y
        'employee_id': fields.many2one('hr.employee', 'Employee Dimension',ondelete='restrict'),#TPT-Y
    }
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.ledger.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_ledger_statement_report_pdf', 'datas': datas}
        
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.ledger.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_ledger_statement_report_xls', 'datas': datas}
    
tpt_general_ledger_from()

class tpt_general_ledger_line(osv.osv_memory):
    _name = "tpt.general.ledger.line"
    _columns = {
        'ledger_id': fields.many2one('tpt.general.ledger.from','General Ledger', ondelete='cascade'),
        'posting_date': fields.date('Posting Date'),
        'order_date': fields.date('Order/work Order Date'),
        'order_no': fields.char('Order/work Order No', size = 1024), #TPT-Y
        'doc_type': fields.char('Document Type', size = 1024),
        'gl_acc': fields.char('GL Code With Description', size = 1024),
        'narration': fields.char('Narration', size = 1024),
        'cost_center': fields.char('Cost Centre', size = 1024),
        'emp': fields.char('Vendor/Customer', size = 1024), #TPT-Y
        'debit': fields.float('Debit',digits=(16,2)),
        'credit': fields.float('Credit',digits=(16,2)),
        'total':fields.float('Total',digits=(16,2)),
        'doc_no_line':fields.char('Document No',size=1024), #TPT-Y
        
                                                        
    }
    
    
tpt_general_ledger_line()

class general_ledger_statement(osv.osv_memory):
    _name = "general.ledger.statement"
    _columns = {    
                'date_from': fields.date('Posting ate From', required=True),
                'date_to': fields.date('To', required=True),
                'account_id':fields.many2one('account.account','GL Account',required=True),
                'doc_type': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Executives Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('ser_inv', 'Service Invoice'),
                                  ('product', 'Production'),
                                  ('staff_payroll', 'Staff Payroll'),
                                  ('worker_payroll', 'Workers Payroll')],'Document Type'),   
#                 'doc_type':fields.selection([('cas_pay','Cash Payment'), ('cas_rec','Cash Receipts'), 
#                                             ('bak_pay','Bank Payments'), ('bak_rec','Bank Receipts'), 
#                                             ('sup_pay','Supplier Payments'),('cus_pay', 'Customer Payments'), 
#                                             ('cus_inv','Customer Invoice'),('deliver','DO'), 
#                                             ('sup_inv','Supplier Invoice'),('grn','GRN'), 
#                                             ('issue','Material Issue'), ('pro','Production'), 
#                                             ('pay','Payroll'),('jour','Journal Vouchers' )],'Document Type'),
                'doc_no':fields.char('Document No',size=1024),
                'narration':fields.char('Narration',size=1024),
                'employee': fields.many2one('res.partner', 'Vendor/Customer',ondelete='restrict'),#TPT-Y
                'cost_center_id':fields.many2one('tpt.cost.center','Cost Center'),#TPT-Y
                'is_posted': fields.boolean('Is Posted'),  #TPT-Y
                'employee_id': fields.many2one('hr.employee', 'Employee Dimension',ondelete='restrict'),#TPT-Y
                
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
    
    def print_report(self, cr, uid, ids, context=None):
        
        def get_emp(move_id):
            acc_obj = self.pool.get('res.partner')
            acc = acc_obj.browse(cr,uid,move_id)
            emp_name = acc.name
            return emp_name
        
        def get_partner(emp_id):
            #emp_id = move_id.id
            if emp_id:
                sql ='''
                     select customer,name,customer_code,vendor_code from res_partner where id = %s
                     '''%(emp_id.id)
                cr.execute(sql)
                for move in cr.dictfetchall():
                     if move['customer'] == 't':
                         if move['customer_code'] and move['name']:
                            partner = move['customer_code'] +'-'+ move['name']
                            return partner or ''
                         elif move['name']:
                             partner = move['name']
                             return partner or ''
                     else:
                             if move['vendor_code'] and move['name']:
                                partner = move['vendor_code'] +'-'+ move['name']
                                return partner or ''
                             elif move['name']:
                                 partner = move['name']
                                 return partner or ''
            
            
        def convert_date_cash(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
        def get_doc_type(doc_type):
            if doc_type == 'cus_inv':
                return "Customer Invoice"
            if doc_type == 'cus_pay':
                return "Customer Payment"
            if doc_type == 'sup_inv_po':
                return "Supplier Invoice(With PO)"
            if doc_type == 'sup_inv':
                return "Supplier Invoice(Without PO)"
            if doc_type == 'sup_pay':
                return "Supplier Payment"
            if doc_type == 'payroll':
                return "Executives Payroll"
            if doc_type == 'staff_payroll':
                return "Staff Payroll"
            if doc_type == 'worker_payroll':
                return "Workers Payroll"
            if doc_type == 'grn':
                return "GRN"
            if doc_type == 'good':
                return "Good Issue"
            if doc_type == 'do':
                return "DO"
            if doc_type == 'inventory':
                return "Inventory Transfer"
            if doc_type == 'manual':
                return "Manual Journal"
            if doc_type == 'cash_pay':
                return "Cash Payment"
            if doc_type == 'cash_rec':
                return "Cash Receipt"
            if doc_type == 'bank_pay':
                return "Bank Payment"
            if doc_type == 'bank_rec':
                return "Bank Receipt"
            if doc_type == 'ser_inv':
                return "Service Invoice"
            if doc_type == 'product':
                return "Production"
            if doc_type == '':
                return "Journal Voucher"
        def get_invoice(cb):
            res = {}
            date_from = cb.date_from
            date_to = cb.date_to
            gl_account = cb.account_id.id
            doc_type = cb.doc_type
            doc_no = cb.doc_no
            narration = cb.narration            
            is_posted = cb.is_posted
            cost_center = cb.cost_center_id.id #TPT-Y
            emp_id=cb.employee.id
            employee_id=cb.employee_id.id
            #emp=cb.employee.name     
            acc_obj = self.pool.get('account.account')
            acc = acc_obj.browse(cr,uid,gl_account)
            acount_move_line_obj = self.pool.get('account.move.line')
            acount_move_obj = self.pool.get('account.move')
            cus_ids = []
            
            sql = '''
            select ml.id from account_move_line ml
            join account_move m on (m.id=ml.move_id)
            left join account_voucher av on (av.move_id = ml.move_id)
            left join tpt_cost_center cc on (cc.id = av.cost_center_id)
            where m.date between '%s' and '%s' and ml.account_id = %s           
            '''%(date_from, date_to, acc.id)
            if doc_type:
                str = " and m.doc_type in('%s')"%(doc_type)
                sql = sql+str
            if doc_no:
                str = " and m.name ~'%s'"%(doc_no)
                sql = sql+str
            if narration:
                str = " and ml.ref ~'%s'"%(narration)
                sql = sql+str            
            if is_posted:
                str = " and m.state = 'posted'"
                sql = sql+str
            if emp_id:
                str = " and ml.partner_id = %s"%(emp_id)
                sql = sql+str
            if employee_id:
                str = " and av.employee_id = %s"%(employee_id)
                sql = sql+str
            if cost_center:
                str = " and cc.id = %s"%(cost_center)
                sql = sql+str
                
            sql=sql+" order by m.date,m.name"
        
            cr.execute(sql)
            cus_ids = [r[0] for r in cr.fetchall()]
            return acount_move_line_obj.browse(cr,uid,cus_ids)
            
            #Commented by TPT-Y on 12/08/2015 
            #===================================================================
            # if is_posted is True: #MAJOR IF
            #     
            #     
            #     if doc_no :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s
            #         order by m.date,m.name  
            #         '''%(date_from, date_to,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif narration :
            #         sql = '''
            #              select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,acc.id,narration)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and narration:
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_no,acc.id,narration)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_type :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.doc_type in('%s') and m.state = 'posted' and ml.account_id = %s
            #         order by m.date,m.name   
            #         '''%(date_from, date_to,doc_type,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif narration and doc_type :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.doc_type in('%s') and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_type,acc.id,doc_no)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and doc_type :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.state = 'posted' and m.date between '%s' and '%s' and m.doc_type in('%s') 
            #         and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s
            #         order by m.date,m.name 
            #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and doc_type and narration:
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)
            #         where state = 'posted' and date between '%s' and '%s' 
            #         and doc_type in('%s') and name ~'%s' and state = 'posted'
            #         and account_id = %s and ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     else:
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)
            #         where m.state = 'posted' and m.date between '%s' and '%s' 
            #         and m.state = 'posted' and ml.account_id = %s
            #         order by m.date,m.name
            #         '''%(date_from, date_to,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            # else: # MAJOR ELSE
            #     if doc_no :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)
            #         where m.date between '%s' and '%s' and m.name ~'%s' 
            #         and ml.account_id = %s
            #         order by m.date,m.name  
            #         '''%(date_from, date_to,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif narration :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)
            #         where m.date between '%s' and '%s' and ml.account_id = %s 
            #         and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,acc.id,narration)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and narration:
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)  
            #         where m.date between '%s' and '%s' and m.name ~'%s' 
            #         and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_no,acc.id,narration)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_type :
            #         sql = '''
            #            select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)  
            #         where m.date between '%s' and '%s' and m.doc_type in('%s') 
            #         and ml.account_id = %s
            #         order by m.date,m.name    
            #         '''%(date_from, date_to,doc_type,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif narration and doc_type :
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)  
            #         where m.date between '%s' and '%s' and m.doc_type in('%s') 
            #         and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_type,acc.id,doc_no)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and doc_type :
            #         sql = '''
            #              select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id) 
            #         where m.date between '%s' and '%s' and m.doc_type in('%s') 
            #         and m.name ~'%s' and ml.account_id = %s
            #         order by m.date,m.name  
            #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     elif doc_no and doc_type and narration:
            #         sql = '''
            #              select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)  
            #         where m.date between '%s' and '%s' and m.doc_type in('%s') 
            #         and m.name ~'%s' and ml.account_id = %s and ml.ref ~'%s'
            #         order by m.date,m.name
            #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            #     else:
            #         sql = '''
            #             select ml.id from account_move_line ml
            #         join account_move m on (m.id=ml.move_id)  
            #         where m.date between '%s' and '%s' and ml.account_id = %s
            #         order by m.date,m.name
            #         '''%(date_from, date_to,acc.id)
            #         cr.execute(sql)
            #         cus_ids = [r[0] for r in cr.fetchall()]
            # return acount_move_line_obj.browse(cr,uid,cus_ids)
            #===================================================================
        def get_voucher(cb,move_id):
            gl_account = cb.account_id.id
            acc_obj = self.pool.get('account.account')
            sql = '''
                select cost_center_id from account_voucher where move_id =%s
            '''%(move_id)
            cr.execute(sql)
            p = cr.fetchone()
            cost_center = ''
            if p and p[0]:
                cost_center = self.pool.get('tpt.cost.center').browse(cr,uid, p[0]).name
            return cost_center
        def get_total(cash,type):
            sum = 0.0
            for line in cash:
                if type == 'credit':
                    sum += line.credit
                if type == 'debit':
                    sum += line.debit
            return sum 
        
         #TPT-Y
        def get_balance(get_invoice):
            credit = 0.0
            debit = 0.0
            for line in get_invoice:
                debit += line.debit
                credit += line.credit
            balance = float(debit) - float(credit)
            balance = float(balance)
            return balance
        
        def get_pur_doc_no(move_id):
            sql = '''select name from purchase_order where id in (select purchase_id from account_invoice where move_id = %s)
            '''%(move_id)
            cr.execute(sql)
            pur_doc_no = cr.fetchone()
            return pur_doc_no and pur_doc_no[0] or ''     
            
        def get_gl_acct(o):            
            gl_account = o.account_id
            gl_act = gl_account.code +''+gl_account.name
            return gl_act
        #TPT-Y
        
           
        cr.execute('delete from tpt_general_ledger_from')
        cb_obj = self.pool.get('tpt.general.ledger.from')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        for line in get_invoice(cb):
            cb_line.append((0,0,{
                    'doc_no_line': line.move_id and line.move_id.name, #TPT-Y             
                    'posting_date': line.move_id and line.move_id.date or False,
                    'order_date': line.move_id and line.move_id.date or False,
                    'order_no': get_pur_doc_no(line.move_id.id), #TPT-Y
                    'doc_type': get_doc_type(line.move_id.doc_type),
                    #'gl_acc': line.account_id.code +' '+ line.account_id.name , #Comment by TPT-Y
                    'narration': line.move_id.ref,
                    'emp': get_partner(line.partner_id) or False, #line.partner_id.name,#TPT-Y
                    'cost_center': get_voucher(cb, line.move_id.id),
                    'debit': line.debit,
                    'credit': line.credit,
            }))
        cb_line.append((0,0,{
            'narration': 'Total',
            'debit': get_total(get_invoice(cb),'debit'),
            'credit': get_total(get_invoice(cb),'credit'),
        }))
        cb_line.append((0,0,{   
            'narration': 'Balance', 
            'credit': get_balance(get_invoice(cb)),  #TPT-Y 
        }))
        vals = {
            'name': 'General Ledger Statement',
            'date_from_title': 'Date From: ', #TPT-Y
            'date_to_title': 'Date To: ', #TPT-Y
            'gl_code_desc': 'GL Code With Description  : ', #TPT-Y
            'emp_desc': 'Employee Dimension  : ', 
            'account_id': cb.account_id and cb.account_id.id or False,
            'doc_type': cb.doc_type and cb.doc_type or False,
            'doc_no':cb.doc_no and cb.doc_no or False,
            'employee':cb.employee.id, #get_emp(cb.employee.id), #cb.employee,#TPT-Y
            'employee_id':cb.employee_id.id,
            'cost_center_id':cb.cost_center_id.id,#TPT-Y
            'narration':cb.narration and cb.narration or False,
            'date_from': cb.date_from,
            'date_to': cb.date_to,
            'gl_desc': get_gl_acct(cb), #TPT-Y
            'is_posted': cb.is_posted,
            'general_ledger_line': cb_line,
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_general_ledger_from')
        return {
                    'name': 'General Ledger Statement',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.general.ledger.from',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }


general_ledger_statement()