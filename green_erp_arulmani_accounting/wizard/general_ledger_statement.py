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
                                  ('worker_payroll', 'Workers Payroll'),
                                  ('stock_adj_inc', 'Stock Adjustment Increase'),
                                  ('stock_adj_dec', 'Stock Adjustment Decrease')
                                  ],'Document Type'),   
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
        'total':fields.float('Transaction Total',digits=(16,2)),
        'doc_no_line':fields.char('Document No',size=1024), #TPT-Y
        'employee_id': fields.char('Employee', size = 1024), #TPT-Y
        'order_id':fields.many2one('purchase.order','Order/work Order No'),
        'move_id':fields.many2one('account.move','Document No'),
        'partner_id':fields.many2one('res.partner','Vendor/Customer'),
                                                        
    }
    
    
tpt_general_ledger_line()

class general_ledger_statement(osv.osv_memory):
    _name = "general.ledger.statement"
    _columns = {    
                'date_from': fields.date('Posting Date From', required=True),
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
                                  ('worker_payroll', 'Workers Payroll'),
                                  ('stock_adj_inc', 'Stock Adjustment Increase'),
                                  ('stock_adj_dec', 'Stock Adjustment Decrease')
                                  ],'Document Type'),   
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
        
        #TPT-Y on 22/09/2015
        def get_total(cash):
            sum = 0.0
            for line in cash:
                sum += line.credit
            return sum 
        
        #TPT-Y on 22/09/2015
        def get_total_debit(get_move_ids, get_opening_balance):
            debit = 0.0
            for move in get_move_ids:
                debit += move['debit']    
            #return debit+get_opening_balance
            return debit # TPT BY RAKESH KUMAR ON 09/02/2016 FOR TOTAL AMOUNT CHANGE
        
         #TPT START BY P.VINOTHKUMAR ON 01/03/2016 for calculate closing balance credit
        def get_total_balance_cr(get_move_ids, get_opening_balance):
            debit = 0.0
            credit = 0.0
            balance = 0.0
            for move in get_move_ids:
                debit += move['debit']
                credit += move['credit']      
            balance = float(debit) - float(credit)
            if get_opening_balance < 0:
               balance = float(balance) + get_opening_balance #TPT START BY P.VINOTHKUMAR ON 02/03/2016
            else:   
               balance = 0.00  
            return balance    
       #TPT END
       
        #TPT START BY P.VINOTHKUMAR ON 01/03/2016 for calculate closing balance debit
        def get_total_balance_dr(get_move_ids, get_opening_balance):
            debit = 0.0
            credit = 0.0
            balance = 0.0
            for move in get_move_ids:
                debit += move['debit']
                credit += move['credit']      
            balance = balance = float(debit) - float(credit)
            if get_opening_balance > 0:
               balance=float(balance)+ get_opening_balance #TPT START BY P.VINOTHKUMAR ON 02/03/2016
            elif get_opening_balance == 0: #TPT START BY P.VINOTHKUMAR ON 02/03/2016 for 0 in opening balance
                balance = float(balance)   
            else:
               balance = 0.00   
            return balance   
      #TPT END      
        
        #TPT-Y on 22/09/2015
        def get_total_balance(get_move_ids, get_opening_balance):
            debit = 0.0
            credit = 0.0
            balance = 0.0
            for move in get_move_ids:
                debit += move['debit']
                credit += move['credit']      
            #balance = (debit+get_opening_balance) - credit
            balance = (debit - credit) # TPT BY RAKESH KUMAR ON 09/02/2016 FOR BALANCE AMOUNT CHANGE
            return balance 
        
        #TPT-Y on 22/09/2015
        def get_opening_balance(o):  
            date_from = o.date_from            
            gl_account = o.account_id.id
            is_posted = o.is_posted            
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            
            sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    left join account_voucher av on (av.move_id = aml.move_id)
                    left join tpt_cost_center cc on (cc.id = av.cost_center_id)                  
                    where am.date < '%s' and aml.account_id = %s
                 '''%(date_from,gl_account)            
            if is_posted:
                str = " and am.state in ('posted')"
                sql = sql+str            
            cr.execute(sql)
            for move in cr.dictfetchall():
                credit += move['credit']               
                    
            sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    left join account_voucher av on (av.move_id = aml.move_id)
                    left join tpt_cost_center cc on (cc.id = av.cost_center_id)                   
                    where am.date < '%s' and aml.account_id = %s
                '''%(date_from,gl_account)
            if is_posted:
                str = " and am.state in ('posted')"
                sql = sql+str                  
            cr.execute(sql)
            for move in cr.dictfetchall():
                debit += move['debit']                  
            balance = debit - credit            
            return balance
                
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
            if doc_type == 'stock_adj_inc':
                return "Stock Adjustment - Increase"
            if doc_type == 'stock_adj_dec':
                return "Stock Adjustment - Decrease"
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
            

        #=======================================================================
        # # TPT-Y, fix-3127 on 31Aug2015
        # def get_voucher(cb,move_id):            
        #     sql = '''
        #         select cost_center_id from account_invoice where move_id =%s
        #     '''%(move_id)
        #     cr.execute(sql)
        #     p = cr.fetchone()
        #     cost_center = ''
        #     if p and p[0]:
        #         cost_center = self.pool.get('tpt.cost.center').browse(cr,uid, p[0]).name
        #     return cost_center
        #=======================================================================
        # TPT START-P.vinothkumar, on 29/01/2016
        def get_voucher(cb,move_id,doc_type):
            if doc_type in ['sup_inv', 'sup_pay','ser_inv', 'sup_inv_po']:
                sql='''select cost_center_id from account_invoice where move_id =%s'''%(move_id)
            if doc_type in ['good']: # TPT-BM-23/05/2016 - TO DISPLAY COST CENTER FOR MATERIAL ISSUE TRANSACTION
                sql='''select cc.id from account_move am
                inner join tpt_material_issue mi on am.ref=mi.doc_no
                left join tpt_cost_center cc on mi.cost_center_id=cc.id 
                where am.id =%s'''%(move_id)
            else: 
                sql='''select cost_center_id from account_voucher where move_id =%s'''%(move_id)    
            cr.execute(sql)
            p = cr.fetchone()
            cost_center = ''
            if p and p[0]:
                cost_center = self.pool.get('tpt.cost.center').browse(cr, uid, p[0]).name
                return cost_center
        # TPT END
        
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
        def get_po_id(move_id):
            sql = '''select id from purchase_order where id in (select purchase_id from account_invoice where move_id = %s)
            '''%(move_id)
            cr.execute(sql)
            po_id = cr.fetchone()
            return po_id and po_id[0] or ''   
            
        def get_gl_acct(o):            
            gl_account = o.account_id
            gl_act = gl_account.code +''+gl_account.name
            return gl_act
        #TPT-Y
        def get_employee_id(cb,move_id):
            employee_id = cb.employee_id
            if employee_id:
                return employee_id.employee_id+'-'+employee_id.name or ''
            else:
                return ''
        def get_line_employee_id(cb,move_id):
            if move_id:
                av_obj = self.pool.get('account.voucher')
                av_obj_ids = av_obj.search(cr, uid, [('move_id','=',move_id)])
                if av_obj_ids:
                    av_obj1 = av_obj.browse(cr,uid,av_obj_ids[0])
                    if av_obj1.employee_id.employee_id:
                        emp = str(av_obj1.employee_id.employee_id) +'-'+str(av_obj1.employee_id.name)
                        return emp
            else:
                return ''
           
        cr.execute('delete from tpt_general_ledger_from')
        cb_obj = self.pool.get('tpt.general.ledger.from')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        
        # TPT START BALAMURUGAN ON 18/02/2016       
        if get_opening_balance(cb)>0:
            cb_line.append((0,0,{
                 'doc_no_line': False, #TPT-Y on 22/09/2015
                 'employee_id': 'Opening Balance:', #TPT-Y on 22/09/2015
                 'debit': get_opening_balance(cb), #TPT-Y on 22/09/2015
                 'credit': 0.00      # TPT BALAMURUGAN ON 18/02/2016  
                
             }))
        else:
            cb_line.append((0,0,{
                 'doc_no_line': False, #TPT-Y on 22/09/2015
                 'employee_id': 'Opening Balance:', #TPT-Y on 22/09/2015
                 #'debit': get_opening_balance(cb), #TPT-Y on 22/09/2015
                 'debit': 0.00,
                 'credit': abs(get_opening_balance(cb)), ##TPT RK on 18/02/2016 
        # TPT END BALAMURUGAN ON 18/02/2016             
             }))
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
                    'cost_center': get_voucher(cb, line.move_id.id,line.move_id.doc_type),
                    'employee_id': get_line_employee_id(cb, line.move_id.id),
                    'debit': line.debit,
                    'credit': line.credit,
                    'move_id': line.move_id and line.move_id.id or False,   
                    'order_id': get_po_id(line.move_id.id) or False,  
                    'partner_id': line.partner_id and line.partner_id.id or False,  
            }))
        cb_line.append((0,0,{
            'narration': 'Total Transaction',
            #'debit': get_total(get_invoice(cb),'debit'),
            'debit': get_total_debit(get_invoice(cb), get_opening_balance(cb)),# TPT START BALAMURUGAN ON 18/02/2016  
            'credit': get_total(get_invoice(cb)), # TPT START BALAMURUGAN ON 18/02/2016  
        }))
        cb_line.append((0,0,{   
            'narration': 'Closing Balance', 
            #'credit': get_balance(get_invoice(cb)),  #TPT-Y
            'credit': get_total_balance_cr(get_invoice(cb), get_opening_balance(cb)), # TPT START BALAMURUGAN ON 18/02/2016   #TPT START BY P.VINOTHKUMAR ON 01/03/2016 for calculate closing balance credit (modify method name)
            'debit': get_total_balance_dr(get_invoice(cb), get_opening_balance(cb)),   #TPT START BY P.VINOTHKUMAR ON 01/03/2016 for calculate closing balance debit 
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