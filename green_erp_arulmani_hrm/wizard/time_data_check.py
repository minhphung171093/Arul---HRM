# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class time_data_check(osv.osv_memory):
    _name = "time.data.check"

    def check_time_data(self, cr, uid, ids, context=None): 
        sql = '''
                update arul_hr_punch_in_out_time set a_shift_count1=1,total_shift_worked1=1 where id in (
                select io.id
                from arul_hr_punch_in_out_time io
                inner join hr_employee emp on io.employee_id=emp.id
                 where  
                io.a_shift_count1=0 and io.g1_shift_count1 =0 
                and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
                io.total_shift_worked1 =0 and io.total_hours<10    and actual_work_shift_id=
                (select id from arul_hr_capture_work_shift where code='A')  )

                '''
        cr.execute(sql)
        
        sql = '''
                update arul_hr_punch_in_out_time set b_shift_count1=1,total_shift_worked1=1 where id in (
                select io.id
                from arul_hr_punch_in_out_time io
                inner join hr_employee emp on io.employee_id=emp.id
                 where  
                io.a_shift_count1=0 and io.g1_shift_count1 =0 
                and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
                io.total_shift_worked1 =0 and io.total_hours<10 and  io.total_hours>7.75  and actual_work_shift_id=
                (select id from arul_hr_capture_work_shift where code='B')  )
        '''
        cr.execute(sql)
        
        sql = '''
                update arul_hr_punch_in_out_time set g1_shift_count1=1,total_shift_worked1=1 where id in (
                select io.id
                from arul_hr_punch_in_out_time io
                inner join hr_employee emp on io.employee_id=emp.id
                 where  
                io.a_shift_count1=0 and io.g1_shift_count1 =0 
                and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
                io.total_shift_worked1 =0 and io.total_hours<12.8 and  io.total_hours>7.75  and actual_work_shift_id=
                (select id from arul_hr_capture_work_shift where code='G1')  )
        '''
        cr.execute(sql)
        
        sql = '''
                update arul_hr_punch_in_out_time set g2_shift_count1=1,total_shift_worked1=1 where id in (
                select io.id
                from arul_hr_punch_in_out_time io
                inner join hr_employee emp on io.employee_id=emp.id
                 where  
                io.a_shift_count1=0 and io.g1_shift_count1 =0 
                and io.g2_shift_count1 =0  and io.b_shift_count1 =0  and io.c_shift_count1 =0  and 
                io.total_shift_worked1 =0 and io.total_hours<12 and  io.total_hours>7.30  and actual_work_shift_id=
                (select id from arul_hr_capture_work_shift where code='G2')  )
        '''
        cr.execute(sql)
        
        return {'type': 'ir.actions.act_window_close'}  
        
time_data_check()

