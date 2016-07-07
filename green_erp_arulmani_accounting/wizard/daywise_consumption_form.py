# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class daywise_consumption_report(osv.osv_memory):
    _name = "daywise.consumption.report"
    
    _columns = {
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'product_id': fields.many2one('product.product','Raw Materials'),
                'name': fields.many2one('mrp.bom','Norms', required=True), 
                'consumption_line': fields.one2many('daywise.consumption.line', 'daywise_id', 'DayWise Consumptions Line'),                       
               }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'daywise.consumption.report' #'day.wise.register'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daywise_consumptions_report_xls', 'datas': datas}

    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'day.wise.register'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daywise_consumptions_report_pdf', 'datas': datas}

daywise_consumption_report()

class daywise_consumption_line(osv.osv_memory):
    _name = "daywise.consumption.line"
    _columns = {
        'daywise_id': fields.many2one('daywise.consumption.report', 'Daywise Consumptions',ondelete='cascade'),
        'material_code': fields.char('Material Code'),
        'material_name': fields.char('Material Name',size=64),
        'uom': fields.char('Unit Of Measure'),
        'date_1': fields.char('Date_1'),
        'date_2': fields.char('Date_2'),
        'date_3': fields.char('Date_3'),
        'date_4': fields.char('Date_4'),
        'date_5': fields.char('Date_5'),
        'date_6': fields.char('Date_6'),
        'date_7': fields.char('Date_7'),
        'date_8': fields.char('Date_8'),
        'date_9': fields.char('Date_9'),
        'date_10': fields.char('Date_10'),
        'date_11': fields.char('Date_11'),
        'date_12': fields.char('Date_12'),
        'date_13': fields.char('Date_13'),
        'date_14': fields.char('Date_14'),
        'date_15': fields.char('Date_15'),
        'date_16': fields.char('Date_16'),
        'date_17': fields.char('Date_17'),
        'date_18': fields.char('Date_18'),
        'date_19': fields.char('Date_19'),
        'date_20': fields.char('Date_20'),
        'date_21': fields.char('Date_21'),
        'date_22': fields.char('Date_22'),
        'date_23': fields.char('Date_23'),
        'date_24': fields.char('Date_24'),
        'date_25': fields.char('Date_25'),
        'date_26': fields.char('Date_26'),
        'date_27': fields.char('Date_27'),
        'date_28': fields.char('Date_28'),
        'date_29': fields.char('Date_29'),
        'date_30': fields.char('Date_30'),
        'date_31': fields.char('Date_31'),
        'total': fields.char('Total'),
    }

daywise_consumption_line()



class day_wise_register(osv.osv_memory):
    _name = "day.wise.register"
    
    _columns = {
            'date_from': fields.date('Date From', required=True),
            'date_to': fields.date('Date To', required=True), 
            'name': fields.many2one('mrp.bom','Norms', required=True),
            'product_id': fields.many2one('product.product','Raw Materials'),      
            
    }

#     def _check_date(self, cr, uid, ids, context=None):
#         for date in self.browse(cr, uid, ids, context=context):
#             if date.date_to < date.date_from:
#                 raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
#                 return False
#         date_format = "%Y-%m-%d"
#         date_from = datetime.strptime(date.date_from, date_format)
#         date_to = datetime.strptime(date.date_to, date_format)
#         days_diff = date_to - date_from 
#         if days_diff.days >=15 :
#                    raise osv.except_osv(_('Warning!'), _('Dates difference is not greater or lesser than 15 days!.'))
#         return True
#     _constraints = [
#         (_check_date, 'Identical Data', []),
#     ]

    #TPT START - By P.vinothkumar and BM - ON 03/06/2016 - FOR (Display To date automatically i.e. From date + 30 days)
    def onchange_from_date(self, cr, uid, ids,date_from=False, context=None):
        vals = {}
        if date_from:
            date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')           
            date_from=str(date_from + timedelta(days=29))[:10]
            vals = {'date_to':date_from,
                    }
            return {'value': vals}
    #TPT END           
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
        
        def get_norms(cb):
        #wizard_data = self.localcontext['data']['form']
            norms=cb.name.id
            #print norms
            sql = '''
                   Select name as norm_name from mrp_bom where id = %s
                  '''%(norms[0])
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                 norm_name1 = move['norm_name']             
            return norm_name1 or ''
    
        def get_raw_mat(cb):
            #wizard_data = self.localcontext['data']['form']
            raw = cb.product_id.id
            #print raw[0]
            if raw:
                sql = '''
                       select default_code as code,name_template as name from product_product where cate_name = 'raw' and id = '%s'
                      '''%(raw[0])
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                     code = move['code']
                     name = move['name']           
                return code +" " +name or ''
            else:
                return ' '
            
#TPT START - Commented By P.vinothkumar - ON 04/05/2016 - OLD Logic - Refer this method: "get_day_cons"        
#         def get_leave_balance(cb):
#             #wizard_data = self.localcontext['data']['form']
#             date_from = cb.date_from
#             date_to = cb.date_to      
#             raw_mat=cb.product_id.id
#             print raw_mat
#             norms= cb.name.id
#             print norms
#             res = []
#             #date_from += datetime.timedelta(1)
#             #datenext = wizard_data['date_from'] + 1
#             
#             if raw_mat:
#                 sql = '''
#                            select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
#                            a.sch_date as scheduled_date,a.app_qty as applied_qty
#                            from (select p.default_code as material_code,p.name_template as material_name,
#                            mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
#                            from mrp_production_product_line mpp
#                            join mrp_production mp on (mp.id = mpp.production_id)
#                            join product_product p on (p.id = mpp.product_id) 
#                            join mrp_bom bm on (bm.id = mp.bom_id)
#                            join product_uom u on (u.id = mpp.product_uom)
#                            where mp.date_planned between '%s' and '%s' 
#                            and mp.bom_id = '%s' and p.id = '%s'and mp.state = 'done'
#                            group by p.default_code,p.name_template,mp.date_planned,
#                            u.name,mpp.product_qty
#                            )a
#                            order by a.material_code,a.sch_date
#                             '''%(date_from,date_to,norms,raw_mat)
#                 cr.execute(sql)                    
#                 lst_val = []
#                 final_data = []
#                 count = 0
#                 for i in cr.dictfetchall():    
#                     if i['mat_code'] in lst_val:
#                         count += 1
#                         val_str = 'applied_qty' + str(count)
#                         data[val_str] = i['applied_qty']        
#                     else:
#                         data = {}
#                         data.update(i)
#                         lst_val.append(i['mat_code'])
#                         count = 0
#                     if not final_data:
#                         final_data.append(data)
#                     else:
#                         l_data = len(final_data)
#                         for pos, val in enumerate(final_data):
#                             if val['mat_code'] == i['mat_code']:
#                                 del final_data[pos]
#                                 final_data.append(data)
#                             else:
#                                 if pos == (l_data - 1):
#                                     final_data.append(data)
#                                 else:
#                                     continue
#                 for pos, val in enumerate(final_data):
#                     for r in range(1,15):
#                         m_str = 'applied_qty' + str(r)
#                         if m_str not in val:
#                             final_data[pos][m_str] = 0.0           
#                 return final_data
#             
#             else:
#                 sql = '''
#                         select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
#                            a.sch_date as scheduled_date,a.app_qty as applied_qty
#                            from (select p.default_code as material_code,p.name_template as material_name,
#                            mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
#                            from mrp_production_product_line mpp
#                            join mrp_production mp on (mp.id = mpp.production_id)
#                            join product_product p on (p.id = mpp.product_id) 
#                            join mrp_bom bm on (bm.id = mp.bom_id)
#                            join product_uom u on (u.id = mpp.product_uom)
#                            where mp.date_planned between '%s' and '%s' 
#                            and mp.bom_id = '%s' and mp.state = 'done'
#                            group by p.default_code,p.name_template,mp.date_planned,
#                            u.name,mpp.product_qty
#                            )a
#                            order by a.material_code,a.sch_date
#                             '''%(date_from,date_to,norms)
#                 cr.execute(sql)         
#                 lst_val = []
#                 final_data = []
#                 count = 0
#                 for i in cr.dictfetchall():    
#                     if i['mat_code'] in lst_val:
#                         count += 1
#                         val_str = 'applied_qty' + str(count)
#                         data[val_str] = i['applied_qty']        
#                     else:
#                         data = {}
#                         data.update(i)
#                         lst_val.append(i['mat_code'])
#                         count = 0
#                     if not final_data:
#                         final_data.append(data)
#                     else:
#                         l_data = len(final_data)
#                         for pos, val in enumerate(final_data):
#                             if val['mat_code'] == i['mat_code']:
#                                 del final_data[pos]
#                                 final_data.append(data)
#                             else:
#                                 if pos == (l_data - 1):
#                                     final_data.append(data)
#                                 else:
#                                     continue
#                 for pos, val in enumerate(final_data):
#                     for r in range(1,15):
#                         m_str = 'applied_qty' + str(r)
#                         if m_str not in val:
#                             final_data[pos][m_str] = 0.0           
#                 return final_data
        
        
       #TPT START - By P.vinothkumar - ON 04/05/2016 - FOR (Display quantities as per day wise)
        def get_day_cons(cb):
            #wizard_data = self.localcontext['data']['form']
            date_from = cb.date_from
            date_to = cb.date_to      
            raw_mat=cb.product_id.id
            norms= cb.name.id
            res = []
 
            sql = '''
            SELECT to_char(generate_series, 'YYYY-MM-DD') as date FROM generate_series('%s'::timestamp,'%s', '1 Days')
            '''%(cb.date_from, cb.date_to)
            cr.execute(sql)
            date_list = [r[0] for r in cr.fetchall()] 
            if len(date_list)< 28 or len(date_list) > 31 :
                raise osv.except_osv(_('Warning!'), _('Date ranges are not greater or lesser than 28 days!.'))
            
            temp_prd_list = []
            sql = '''
            select distinct mpl.product_id as product_id, pro.default_code  from mrp_production_product_line mpl
            inner join mrp_production mp on mpl.production_id=mp.id
            inner join product_product pro on mpl.product_id=pro.id
            where mp.bom_id=%s and mp.date_planned between '%s' and '%s'
            order by pro.default_code
            '''%(norms, cb.date_from, cb.date_to)
            cr.execute(sql)
            temp_prd_list = cr.dictfetchall()

            if raw_mat:
                temp_prd_list = [{ 'product_id' : raw_mat }]
            for product_list in temp_prd_list:
                sql = '''
                     
                    select coalesce((select default_code from product_product where id=%(product_id)s),'') as material_code,
                    
                    (select coalesce((select name_template from product_product where id=%(product_id)s),'')) as material_name,
                    
                    (select coalesce((select pu.name from product_template pp
                    inner join product_uom pu on pp.uom_po_id=pu.id
                    where pp.id=%(product_id)s),'')) as uom,
                    
                    (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id) 
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date1)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),'0.0')) as applied_qty,
                       
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date2)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty1,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date3)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty2, 
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date4)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty3,
                               
                (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date5)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty4,
                               
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date6)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty5,
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date7)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty6,
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date8)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty7,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date9)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty8, 
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date10)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty9,
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date11)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty10,
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date12)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty11,
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date13)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty12,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date14)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty13, 
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date15)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty14,
                   
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date16)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty15,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date17)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty16, 
                               
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date18)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty17,
                               
                (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date19)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty18,
                               
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date20)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty19,
                               
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date21)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty20,
                               
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date22)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty21,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date23)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty22, 
                               
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date24)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty23,
                               
                 (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date25)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty24,
                               
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date26)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty25,
                               
                  (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date27)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty26,
                               
                   (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date28)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty27                  
                                                                                                                
                    '''%{'bom_id':norms,
                         'date1':date_list[0],
                         'date2':date_list[1],
                         'date3':date_list[2],
                         'date4':date_list[3],
                         'date5':date_list[4],
                         'date6':date_list[5],
                         'date7':date_list[6],
                         'date8':date_list[7],
                         'date9':date_list[8],
                         'date10':date_list[9],
                         'date11':date_list[10],
                         'date12':date_list[11],
                         'date13':date_list[12],
                         'date14':date_list[13],
                         'date15':date_list[14],
                         'date16':date_list[15],
                         'date17':date_list[16],
                         'date18':date_list[17],
                         'date19':date_list[18],
                         'date20':date_list[19],
                         'date21':date_list[20],
                         'date22':date_list[21],
                         'date23':date_list[22],
                         'date24':date_list[23],
                         'date25':date_list[24],
                         'date26':date_list[25],
                         'date27':date_list[26],
                         'date28':date_list[27],
                         'product_id': product_list['product_id'],
                    }
                #  
                #print len(date_list)               
                if len(date_list)==29:
                    sql += '''
                    ,(select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned= '%(date29)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty28 
                    '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'product_id': product_list['product_id'],
                    } 
                    
                #
                if len(date_list)==30:
                        sql += '''
                        ,(select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                                   from mrp_production_product_line mpp
                                   join mrp_production mp on (mp.id = mpp.production_id)
                                   join mrp_bom bm on (bm.id = mp.bom_id)
                                   where mp.date_planned= '%(date29)s'
                                   and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty28,
                        (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                                   from mrp_production_product_line mpp
                                   join mrp_production mp on (mp.id = mpp.production_id)
                                   join mrp_bom bm on (bm.id = mp.bom_id)
                                   where mp.date_planned= '%(date30)s'
                                   and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty29 
                        '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'date30':date_list[29],
                         'product_id': product_list['product_id'],
                    }
                        
                        
                        
                if len(date_list)==31:
                        sql += '''
                        ,(select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                                   from mrp_production_product_line mpp
                                   join mrp_production mp on (mp.id = mpp.production_id)
                                   join mrp_bom bm on (bm.id = mp.bom_id)
                                   where mp.date_planned= '%(date29)s'
                                   and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty28,
                        (select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                                   from mrp_production_product_line mpp
                                   join mrp_production mp on (mp.id = mpp.production_id)
                                   join mrp_bom bm on (bm.id = mp.bom_id)
                                   where mp.date_planned= '%(date30)s'
                                   and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty29
                        ,(select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as app_qty
                                   from mrp_production_product_line mpp
                                   join mrp_production mp on (mp.id = mpp.production_id)
                                   join mrp_bom bm on (bm.id = mp.bom_id)
                                   where mp.date_planned= '%(date31)s'
                                   and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as applied_qty30
                        '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'date30':date_list[29],
                         'date31':date_list[30],
                         'product_id': product_list['product_id'],
                    }
                sql += '''        
               ,(select coalesce((select case when sum(mpp.product_qty)>=0 then sum(mpp.product_qty) else 0 end as total
                               from mrp_production_product_line mpp
                               join mrp_production mp on (mp.id = mpp.production_id)
                               join mrp_bom bm on (bm.id = mp.bom_id)
                               where mp.date_planned between '%(from_date)s' and '%(to_date)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and mpp.product_id=%(product_id)s),0)) as total  
                 '''%{
                      'from_date':cb.date_from, 
                      'to_date': cb.date_to,
                      'bom_id':norms,
                      'product_id': product_list['product_id'],
                    }                       
                        
                #print sql
                cr.execute(sql) 
                #print sql
                res += cr.dictfetchall()
                    
            return res
        #TPT END#
        #TPT START - By P.vinothkumar - ON 09/06/2016 - FOR (Display quantities as per day wise)
        def new_get_day_cons(cb):
            #wizard_data = self.localcontext['data']['form']
            date_from = cb.date_from
            date_to = cb.date_to      
            raw_mat=cb.product_id.id
            norms= cb.name.id
            res = []
 
            sql = '''
            SELECT to_char(generate_series, 'YYYY-MM-DD') as date FROM generate_series('%s'::timestamp,'%s', '1 Days')
            '''%(cb.date_from, cb.date_to)
            cr.execute(sql)
            date_list = [r[0] for r in cr.fetchall()] 
            if len(date_list)< 28 or len(date_list) > 31 :
                raise osv.except_osv(_('Warning!'), _('Date ranges are not greater or lesser than 28 days!.'))
            
            temp_prd_list = []
            sql = '''
            select distinct sm.product_id as product_id, pro.default_code from mrp_production mp
            inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
            inner join stock_move sm on mpm.move_id=sm.id
            inner join product_product pro on sm.product_id=pro.id
            where mp.bom_id=%s and mp.date_planned between '%s' and '%s'
            order by pro.default_code
            '''%(norms, cb.date_from, cb.date_to)
            cr.execute(sql)
            temp_prd_list = cr.dictfetchall()

            if raw_mat:
                temp_prd_list = [{ 'product_id' : raw_mat }]
            for product_list in temp_prd_list:
                sql = '''
                     
                    select coalesce((select default_code from product_product where id=%(product_id)s),'') as material_code,
                    
                    (select coalesce((select name_template from product_product where id=%(product_id)s),'')) as material_name,
                    
                    (select coalesce((select pu.name from product_template pp
                    inner join product_uom pu on pp.uom_po_id=pu.id
                    where pp.id=%(product_id)s),'')) as uom,
                    
                    (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date1)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty,
                       
                   (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date2)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty1,
                               
                   (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date3)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty2, 
                               
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date4)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty3,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date5)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty4,
                               
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date6)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty5,
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date7)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty6,
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date8)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty7,
                               
                   (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date9)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty8, 
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date10)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty9,
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date11)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty10,
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date12)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty11,
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date13)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty12,
                               
                   (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date14)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty13,
                               
                   (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date15)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty14,
                   
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date16)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty15,
                               
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date17)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty16, 
                               
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date18)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty17,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date19)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty18,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date20)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty19,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date21)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty20,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date22)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty21,
                               
                (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date23)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty22, 
                               
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date24)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty23,
                               
                 (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date25)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty24,
                               
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date26)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty25,
                               
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date27)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty26,
                               
                  (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date28)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty27                 
                                                                                                                
                    '''%{'bom_id':norms,
                         'date1':date_list[0],
                         'date2':date_list[1],
                         'date3':date_list[2],
                         'date4':date_list[3],
                         'date5':date_list[4],
                         'date6':date_list[5],
                         'date7':date_list[6],
                         'date8':date_list[7],
                         'date9':date_list[8],
                         'date10':date_list[9],
                         'date11':date_list[10],
                         'date12':date_list[11],
                         'date13':date_list[12],
                         'date14':date_list[13],
                         'date15':date_list[14],
                         'date16':date_list[15],
                         'date17':date_list[16],
                         'date18':date_list[17],
                         'date19':date_list[18],
                         'date20':date_list[19],
                         'date21':date_list[20],
                         'date22':date_list[21],
                         'date23':date_list[22],
                         'date24':date_list[23],
                         'date25':date_list[24],
                         'date26':date_list[25],
                         'date27':date_list[26],
                         'date28':date_list[27],
                         'product_id': product_list['product_id'],
                    }
                #  
                #print len(date_list)               
                if len(date_list)==29:
                    sql += '''
                    ,(select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date29)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty28 
                    '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'product_id': product_list['product_id'],
                    } 
                    
                #
                if len(date_list)==30:
                        sql += '''
                        ,(select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date29)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty28,
                        (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date30)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty29
                        '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'date30':date_list[29],
                         'product_id': product_list['product_id']
                    }
                        
                        
                        
                if len(date_list)==31:
                        sql += '''
                        ,(select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date29)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty28,
                        (select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date30)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty29
                        ,(select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as app_qty
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned= '%(date31)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),'0.0')) as applied_qty30
                        '''%{'bom_id':norms,
                         'date29':date_list[28],
                         'date30':date_list[29],
                         'date31':date_list[30],
                         'product_id': product_list['product_id']
                    }
                sql += '''        
               ,(select coalesce((select case when sum(sm.product_qty)>=0 then sum(sm.product_qty) else 0 end as total
                               from mrp_production mp
                               inner join mrp_production_move_ids mpm on mp.id=mpm.production_id
                               inner join stock_move sm on mpm.move_id=sm.id
                               where mp.date_planned between '%(from_date)s' and '%(to_date)s'
                               and mp.bom_id = %(bom_id)s and mp.state = 'done' and sm.product_id=%(product_id)s),0)) as total  
                 '''%{
                      'from_date':cb.date_from, 
                      'to_date': cb.date_to,
                      'bom_id':norms,
                      'product_id': product_list['product_id'],
                    }                       
                        
                cr.execute(sql) 
                res += cr.dictfetchall()
                    
            return res 
        #TPT END
        
        #TPT START - By P.vinothkumar - ON 04/05/2016 - FOR (Display quantities as two decimal places and display dates)
        def get_amt(amt):       
            locale.setlocale(locale.LC_NUMERIC, "en_IN")
            inr_comma_format = locale.format("%.3f", amt, grouping=True)
            return inr_comma_format
        
        
        cr.execute('delete from daywise_consumption_report')
        cb_obj = self.pool.get('daywise.consumption.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        sql = '''
            SELECT to_char(generate_series, 'DD/MM/YYYY') as date FROM generate_series('%s'::timestamp,'%s', '1 Days')
            '''%(cb.date_from, cb.date_to)
        cr.execute(sql)
        date_list = [r[0] for r in cr.fetchall()] 
        ##
        date_list_28 = ''
        date_list_29 = ''
        date_list_30 = ''
        if len(date_list)==29:
            date_list_28 = date_list[28]   
        if len(date_list)==30:
            date_list_28 = date_list[28]
            date_list_29 = date_list[29] 
                
        if len(date_list)==31:
            date_list_28 = date_list[28] 
            date_list_29 = date_list[29]
            date_list_30 = date_list[30] 
        ##
        if len(date_list)>=28:
            cb_line.append((0,0,{           
                     'date_1':date_list[0],
                     'date_2':date_list[1],
                     'date_3':date_list[2],
                     'date_4':date_list[3],
                     'date_5':date_list[4],
                     'date_6':date_list[5],
                     'date_7':date_list[6],
                     'date_8':date_list[7],
                     'date_9':date_list[8],
                     'date_10':date_list[9],
                     'date_11':date_list[10],
                     'date_12':date_list[11],
                     'date_13':date_list[12],
                     'date_14':date_list[13],
                     'date_15':date_list[14],
                     'date_16':date_list[15],
                     'date_17':date_list[16],
                     'date_18':date_list[17],
                     'date_19':date_list[18],
                     'date_20':date_list[19],
                     'date_21':date_list[20],
                     'date_22':date_list[21],
                     'date_23':date_list[22],
                     'date_24':date_list[23],
                     'date_25':date_list[24],
                     'date_26':date_list[25],
                     'date_27':date_list[26],
                     'date_28':date_list[27],
                     'date_29':date_list_28,
                     'date_30':date_list_29,
                     'date_31':date_list_30
                     
                 }))
            
        else:
            raise osv.except_osv(_('Warning!'), _('Date ranges are not greater or lesser than 28 days!.')) 
          #TPT END#
           # Method Renamed by P.Vinothkumar on 08/06/2016 for missing products in report
        for line in new_get_day_cons(cb):#get_day_cons(cb):
            applied_qty28 = 0
            applied_qty29 = 0
            applied_qty30 = 0
            if 'applied_qty28' in line:
                applied_qty28 = line['applied_qty28']
            if 'applied_qty29' in line:
                applied_qty28 = line['applied_qty28']
                applied_qty29 = line['applied_qty29']
            if 'applied_qty30' in line:
                applied_qty28 = line['applied_qty28']
                applied_qty29 = line['applied_qty29']
                applied_qty30 = line['applied_qty30']
            cb_line.append((0,0,{
                    'material_code':line['material_code'],
                    'material_name':line['material_name'],
                    'uom':line['uom'],
                    'date_1':get_amt(line['applied_qty']),
                    'date_2':get_amt(line['applied_qty1']),
                    'date_3':get_amt(line['applied_qty2']),
                    'date_4':get_amt(line['applied_qty3']),
                    'date_5':get_amt(line['applied_qty4']),
                    'date_6':get_amt(line['applied_qty5']),
                    'date_7':get_amt(line['applied_qty6']),
                    'date_8':get_amt(line['applied_qty7']),
                    'date_9':get_amt(line['applied_qty8']),
                    'date_10':get_amt(line['applied_qty9']),
                    'date_11':get_amt(line['applied_qty10']),  
                    'date_12':get_amt(line['applied_qty11']),
                    'date_13':get_amt(line['applied_qty12']),
                    'date_14':get_amt(line['applied_qty13']),
                    'date_15':get_amt(line['applied_qty14']),
                    'date_16':get_amt(line['applied_qty15']),
                    'date_17':get_amt(line['applied_qty16']),
                    'date_18':get_amt(line['applied_qty17']),
                    'date_19':get_amt(line['applied_qty18']),
                    'date_20':get_amt(line['applied_qty19']),
                    'date_21':get_amt(line['applied_qty20']),
                    'date_22':get_amt(line['applied_qty21']),
                    'date_23':get_amt(line['applied_qty22']),
                    'date_24':get_amt(line['applied_qty23']),
                    'date_25':get_amt(line['applied_qty24']),  
                    'date_26':get_amt(line['applied_qty25']),
                    'date_27':get_amt(line['applied_qty26']),
                    'date_28':get_amt(line['applied_qty27']),
                    'total':get_amt(line['total']),
                    'date_29':get_amt(applied_qty28),
                    'date_30':get_amt(applied_qty29),
                    'date_31':get_amt(applied_qty30),
                    
            }))                    
        
        vals = {
            'name': 'Day Wise Consumption Report',
            'date_from': cb.date_from,           
            'date_to': cb.date_to,
            'product_id':cb.product_id.id, 
            'name': cb.name.id,
            'consumption_line': cb_line,
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_daywise_consumption_report')
        return {
                    'name': 'Day Wise Consumption Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'daywise.consumption.report',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }
        
day_wise_register()