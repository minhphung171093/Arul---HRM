# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class time_data_upload(osv.osv_memory):
    _name = "time.data.upload"

    def upload_time_data(self, cr, uid, ids, context=None): 
        print "SCHEDULER JOB - STARTED"
        attend_obj = self.pool.get('tpt.hr.attendance') 
        attend_obj_ids = attend_obj.search(cr, uid, [('is_processed','=',False)])  #, ('is_processed','=','f')
        #b_shift_total_time = b_work_shift1.time_total   
        for time_entry in attend_obj.browse(cr,uid,attend_obj_ids):
            employee_id = time_entry.employee_id.id
            work_date = time_entry.work_date
            day = work_date[8:10]
            month = work_date[5:7]
            year = work_date[:4]
            punch_obj = self.pool.get('arul.hr.punch.in.out') 
            
            shift_id = punch_obj.get_work_shift(cr, uid, employee_id, int(day), int(month), year)
            print shift_id
            #
            attend_obj.write(cr, uid, time_entry.id, {'is_processed':'t'})
        return {'type': 'ir.actions.act_window_close'}  
        
time_data_upload()

