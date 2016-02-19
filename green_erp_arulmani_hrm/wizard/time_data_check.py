# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class time_data_check(osv.osv_memory):
    _name = "time.data.check"

    def check_time_data(self, cr, uid, ids, context=None): 
#         sql = '''
#                 update arul_hr_punch_in_out_time set a_shift_count1=1,total_shift_worked1=1 where id in (
#                 select io.id
#                 from arul_hr_punch_in_out_time io
#                 inner join hr_employee emp on io.employee_id=emp.id
#                  where  
#                 io.a_shift_count1=0 and io.g1_shift_count1 =0 
#                 and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
#                 io.total_shift_worked1 =0 and io.total_hours<11.20    and actual_work_shift_id=
#                 (select id from arul_hr_capture_work_shift where code='A')  )
#  
#                 '''
#         cr.execute(sql)
#          
#         sql = '''
#                 update arul_hr_punch_in_out_time set b_shift_count1=1,total_shift_worked1=1 where id in (
#                 select io.id
#                 from arul_hr_punch_in_out_time io
#                 inner join hr_employee emp on io.employee_id=emp.id
#                  where  
#                 io.a_shift_count1=0 and io.g1_shift_count1 =0 
#                 and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
#                 io.total_shift_worked1 =0 and io.total_hours<10 and  io.total_hours>7.75  and actual_work_shift_id=
#                 (select id from arul_hr_capture_work_shift where code='B')  )
#         '''
#         cr.execute(sql)
#          
#         sql = '''
#                 update arul_hr_punch_in_out_time set g1_shift_count1=1,total_shift_worked1=1 where id in (
#                 select io.id
#                 from arul_hr_punch_in_out_time io
#                 inner join hr_employee emp on io.employee_id=emp.id
#                  where  
#                 io.a_shift_count1=0 and io.g1_shift_count1 =0 
#                 and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
#                 io.total_shift_worked1 =0 and io.total_hours<12.8 and  io.total_hours>7.75  and actual_work_shift_id=
#                 (select id from arul_hr_capture_work_shift where code='G1')  )
#         '''
#         cr.execute(sql)
#          
#         sql = '''
#                 update arul_hr_punch_in_out_time set g2_shift_count1=1,total_shift_worked1=1 where id in (
#                 select io.id
#                 from arul_hr_punch_in_out_time io
#                 inner join hr_employee emp on io.employee_id=emp.id
#                  where  
#                 io.a_shift_count1=0 and io.g1_shift_count1 =0 
#                 and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
#                 io.total_shift_worked1 =0 and io.total_hours<12 and  io.total_hours>7.30  and actual_work_shift_id=
#                 (select id from arul_hr_capture_work_shift where code='G2')  )
#         '''
#         cr.execute(sql)
#         sql = '''
#             update arul_hr_permission_onduty set shift_type='G2' where 
#             total_shift_worked=1
#             and EXTRACT(year FROM date) = 2015 AND EXTRACT(month FROM date) = 8
#             and shift_type is null
#         '''
#         cr.execute(sql)
        #TPT-By BalamuruganPurushothaman-ON 18/02/2016-TO CHANGE DOR TO AGE OF 58
        emp_obj = self.pool.get('hr.employee')
        resource_obj = self.pool.get('resource.resource')
        emp_ids = resource_obj.search(cr, uid, [('active','=', True)])
        for emp in emp_obj.browse(cr, uid, emp_ids):
            birthday = emp.birthday
            retirement = ''
            if birthday:
                day = birthday[8:10]
                month = birthday[5:7]
                year = birthday[:4]
                if month == "01" and day=='01':
                    year = int(year)+57
                    num_of_month = calendar.monthrange(year,12)[1]
                    retirement = datetime.datetime(year,12,num_of_month)
                elif month != "01" and day=='01':
                    year = int(year)+58
                    month = int(month)-1
                    num_of_month = calendar.monthrange(year,month)[1]
                    retirement = datetime.datetime(year,month,num_of_month)
                else:
                    year = int(year)+58
                    day = int(day)-1
                    month = int(month)
                    retirement = datetime.datetime(year,month,day)
                if retirement:
                    retirement=retirement.strftime('%Y-%m-%d')
                    vals = {'date_of_retirement':retirement}
                    #emp_obj.write(cr, uid, [emp.id], vals, context)
                    sql = """
                    update hr_employee set date_of_retirement='%s' where id=%s
                    """%(retirement, emp.id)
                    cr.execute(sql)           
        return {'type': 'ir.actions.act_window_close'}  
        
time_data_check()

