# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class monthwise_lop_wizard(osv.osv_memory):
    _name = "monthwise.lop.wizard"
    
    _columns = {
        'year': fields.selection([(num, str(num)) for num in range(2000, 2060)], 'Year'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
    }
    
    _defaults = {
        'year':int(time.strftime('%Y')),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('monthwise.lop.screen')
        
        this = self.browse(cr, uid, ids[0])
        screen_line = []
        data_dict = {}
        emp_arr = []
        emp_data_arr = []
        sql = '''
            select
                emp.id as employee_id, emp.employee_id as code, rr.name as name, emp.last_name as last_name, hrj.name as designation,
                to_char(eld.date_from, 'MM') as month, case when sum(days_total)!=0 then sum(days_total) else 0 end days
            
            from
                arul_hr_employee_leave_details eld
                left join hr_employee emp on eld.employee_id = emp.id
                left join resource_resource rr on emp.resource_id = rr.id
                left join hr_job hrj on emp.job_id = hrj.id
            where eld.state = 'done' 
        '''
        if this.year:
            sql += '''
                and to_char(eld.date_from, 'YYYY')='%s'
            '''%(str(this.year))
        sql += '''
            group by emp.id, emp.employee_id, rr.name, emp.last_name, hrj.name, to_char(eld.date_from, 'MM')
        '''
        cr.execute(sql)
        res = cr.dictfetchall()
        for line in res:
            if line['employee_id'] not in emp_arr:
                emp_arr.append(line['employee_id'])
                emp_data_arr.append(line)
            if data_dict.get(line['employee_id'], False):
                if data_dict[line['employee_id']].get(line['month'], False):
                    data_dict[line['employee_id']][line['month']] += line['days']
                    data_dict[line['employee_id']][line['total']] += line['days']
                else:
                    data_dict[line['employee_id']][line['month']] = line['days']
                    data_dict[line['employee_id']][line['total']] = line['days']
            else:
                data = line
                data.update({line['month']: line['days'], 'total': line['days']})
                data_dict[line['employee_id']] = data
        for seq,line in enumerate(emp_data_arr):
            line_vals = {
                'sequence': seq+1,
                'emp_code': line['code'],
                'emp_name': (line['name'] or '')+' '+(line['last_name'] or ''),
                'designation': line['designation'],
            }
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('01',False):
                line_vals['jan'] = data_dict[line['employee_id']]['01']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('02',False):
                line_vals['feb'] = data_dict[line['employee_id']]['02']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('03',False):
                line_vals['mar'] = data_dict[line['employee_id']]['03']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('04',False):
                line_vals['apr'] = data_dict[line['employee_id']]['04']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('05',False):
                line_vals['may'] = data_dict[line['employee_id']]['05']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('06',False):
                line_vals['june'] = data_dict[line['employee_id']]['06']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('07',False):
                line_vals['july'] = data_dict[line['employee_id']]['07']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('08',False):
                line_vals['aug'] = data_dict[line['employee_id']]['08']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('09',False):
                line_vals['sep'] = data_dict[line['employee_id']]['09']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('10',False):
                line_vals['oct'] = data_dict[line['employee_id']]['10']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('11',False):
                line_vals['nov'] = data_dict[line['employee_id']]['11']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('12',False):
                line_vals['dec'] = data_dict[line['employee_id']]['12']
            if data_dict.get(line['employee_id'], False) and data_dict[line['employee_id']].get('total',False):
                line_vals['total'] = data_dict[line['employee_id']]['total']
            screen_line.append((0,0,line_vals))
        vals = {
            'name': '',
            'screen_line': screen_line,
            'year': this.year,
        }
        
        report_id = report_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_report', 'view_monthwise_lop_screen')
        return {
            'name': 'Monthwise LOP Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'monthwise.lop.screen',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': res and res[1] or False,
            'res_id': report_id,
        }
        
monthwise_lop_wizard()

class monthwise_lop_screen(osv.osv_memory):
    _name = "monthwise.lop.screen"
    
    _columns = {
        'name': fields.char('Name', size=1024),
        'screen_line': fields.one2many('monthwise.lop.screen.line', 'screen_id', 'Line'),
    }
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'monthwise.lop.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'monthwise_lop_report_xls', 'datas': datas}
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'monthwise.lop.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'monthwise_lop_report_pdf', 'datas': datas}
        
monthwise_lop_screen()

class monthwise_lop_screen_line(osv.osv_memory):
    _name = "monthwise.lop.screen.line"
    
    _columns = {
        'screen_id': fields.many2one('monthwise.lop.screen', 'Screen', ondelete='cascade'),
        'employee_id': fields.many2one('monthwise.lop.screen', 'Employee'),
        'sequence': fields.integer('SI.No'),
        'emp_code': fields.char('EMP. CODE', size=1024),
        'emp_name': fields.char('Employee Name', size=1024),
        'designation': fields.char('Designation', size=1024),
        'jan': fields.float("Jan"),
        'feb': fields.float("Feb"),
        'mar': fields.float("Mar"),
        'apr': fields.float("Apr"),
        'may': fields.float("May"),
        'june': fields.float("June"),
        'july': fields.float("July"),
        'aug': fields.float("Aug"),
        'sep': fields.float("Sep"),
        'oct': fields.float("Oct"),
        'nov': fields.float("Nov"),
        'dec': fields.float("Dec"),
        'total': fields.float("Total"),
    }
        
monthwise_lop_screen_line()
