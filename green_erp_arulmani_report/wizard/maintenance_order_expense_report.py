# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class maintenance_order_expense_wizard(osv.osv_memory):
    _name = "maintenance.order.expense.wizard"
    
    _columns = {
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'maintenance_id': fields.many2one('tpt.maintenance.oder', 'Maintenance Order'),
        'notif_type':fields.selection([
                                ('prevent','Preventive Maintenance'),
                                ('break','Breakdown')],'Notification Type'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'section_id': fields.many2one('arul.hr.section', 'Section'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        
        def convert_date(date):
            if date:
                date = datetime.strptime(date, '%Y-%m-%d')
                return date.strftime('%d/%m/%Y')
            return ''
        
        report_obj = self.pool.get('maintenance.order.expense.screen')
        
        this = self.browse(cr, uid, ids[0])
        screen_line = []
        sql = '''
            select
                date(timezone('UTC',mo.create_date)) as date, mo.id as maintenance_id, mo.notif_type as notification_type,
                nti.issue_date as notification_date, nti.name as notification_no, dep.name as department, sec.name as section
            
            from
                tpt_maintenance_oder mo
                left join tpt_notification nti on mo.notification_id = nti.id
                left join hr_department dep on mo.department_id = dep.id
                left join arul_hr_section sec on mo.section_id = sec.id
            where mo.state not in ('draft','cancel') and date(timezone('UTC',mo.create_date)) between '%s' and '%s' 
        '''%(this.date_from,this.date_to)
        if this.maintenance_id:
            sql += '''
                and mo.id=%s
            '''%(this.maintenance_id.id)
        if this.notif_type:
            sql += '''
                and mo.notif_type='%s'
            '''%(this.notif_type)
        if this.department_id:
            sql += '''
                and mo.department_id=%s
            '''%(this.department_id.id)
        if this.section_id:
            sql += '''
                and mo.section_id=%s
            '''%(this.section_id.id)
        cr.execute(sql)
        for seq,line in enumerate(cr.dictfetchall()):
            notification_type = ''
            if line['notification_type']=='prevent':
                notification_type = 'Preventive Maintenance'
            if line['notification_type']=='break':
                notification_type = 'Breakdown'
                
            total_amount = 0
            cost_center = ''
            
            maintenance = self.pool.get('tpt.maintenance.oder').browse(cr, uid, line['maintenance_id'])
            for service in maintenance.third_service_line:
                total_amount += service.grand_total
            
            po_id = maintenance.third_service_line and maintenance.third_service_line[0].third_service_line and maintenance.third_service_line[0].third_service_line[0] and maintenance.third_service_line[0].third_service_line[0].po_id and maintenance.third_service_line[0].third_service_line[0].po_id.id or False
            if po_id:
                sql = '''
                    select name from tpt_cost_center where id in (select cost_center_id from account_invoice where purchase_id=%s and doc_type in ('service_invoice_qty','service_invoice_amt'))
                '''%(po_id)
                cr.execute(sql)
                c = cr.fetchone()
                cost_center = c and c[0] or ''
                
            screen_line.append((0,0,{
                'sequence': seq+1,
                'date': convert_date(line['date']),
                'maintenance_id': line['maintenance_id'],
                'notification_type': notification_type,
                'notification_date': convert_date(line['notification_date']),
                'notification_no': line['notification_no'],
                'department': line['department'],
                'section': line['section'],
                'total_amount': total_amount,
                'cost_center': cost_center,
            }))
        vals = {
            'name': '',
            'screen_line': screen_line,
        }
        
        report_id = report_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_report', 'view_maintenance_order_expense_screen')
        return {
            'name': 'Maintenance Order Expense Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maintenance.order.expense.screen',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': res and res[1] or False,
            'res_id': report_id,
        }
        
maintenance_order_expense_wizard()

class maintenance_order_expense_screen(osv.osv_memory):
    _name = "maintenance.order.expense.screen"
    
    _columns = {
        'name': fields.char('Name', size=1024),
        'screen_line': fields.one2many('maintenance.order.expense.screen.line', 'screen_id', 'Line'),
    }
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'maintenance.order.expense.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'maintenance_order_expense_report_xls', 'datas': datas}
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'maintenance.order.expense.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'maintenance_order_expense_report_pdf', 'datas': datas}
        
maintenance_order_expense_screen()

class maintenance_order_expense_screen_line(osv.osv_memory):
    _name = "maintenance.order.expense.screen.line"
    
    _columns = {
        'screen_id': fields.many2one('maintenance.order.expense.screen', 'Screen', ondelete='cascade'),
        'sequence': fields.integer('SI.No'),
        'date': fields.char('Date', size=1024),
        'maintenance_id': fields.many2one('tpt.maintenance.oder', 'Maintenance Order'),
        'notification_type': fields.char('Notification Type', size=1024),
        'notification_date': fields.char("Notification Date", size=1024),
        'notification_no': fields.char("Notification No", size=1024),
        'department': fields.char("Department", size=1024),
        'section': fields.char("Section", size=1024),
        'total_amount': fields.float("Total Amount"),
        'cost_center': fields.char("Cost Center", size=1024),
    }
        
maintenance_order_expense_screen_line()
