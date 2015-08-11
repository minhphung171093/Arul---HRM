# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
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
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'day.wise.register'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daywise_consumptions_report_xls', 'datas': datas}

    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'day.wise.register'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daywise_consumptions_report_pdf', 'datas': datas}

daywise_consumption_report()

class daywise_consumption_line(osv.osv_memory):
    _name = "daywise.consumption.line"
    _columns = {
        'daywise_id': fields.many2one('daywise.consumption.report', 'Daywise Consumptions'),
        'material_code': fields.char('Material Code'),
        'material_name': fields.char('Material Name',size=64),
        'uom': fields.char('Unit Of Measure'),
        'date_1': fields.float('Date_1'),
        'date_2': fields.float('Date_2'),
        'date_3': fields.float('Date_3'),
        'date_4': fields.float('Date_4'),
        'date_5': fields.float('Date_5'),
        'date_6': fields.float('Date_6'),
        'date_7': fields.float('Date_7'),
        'date_8': fields.float('Date_8'),
        'date_9': fields.float('Date_9'),
        'date_10': fields.float('Date_10'),
        'date_11': fields.float('Date_11'),
        'date_12': fields.float('Date_12'),
        'date_13': fields.float('Date_13'),
        'date_14': fields.float('Date_14'),
        'date_15': fields.float('Date_15'),
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

    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def _check_wiz_date(self, cr, uid, ids, context=None):
        wiz_br = self.browse(cr, uid, ids, context=context)
        if wiz_br.date_from and wiz_br.date_to:
                    date_format = "%Y-%m-%d"
                    date_from = datetime.strptime(wiz_br.date_from, date_format)
                    date_to = datetime.strptime(wiz_br.date_to, date_format)
                    days_diff = date_to - date_from 
        if days_diff.days > 15:
                    raise osv.except_osv(_('Error!'), _('Dates difference is not greater than 15 days!.'))
        elif days_diff.days < 0:
                    raise osv.except_osv(_('Error!'), _('date2(%s) is less than date1(%s)!.') % (wiz_br.date_to,wiz_br.date_from,))
                    
        
    
    def print_report(self, cr, uid, ids, context=None):
        def get_norms(cb):
            norms=cb.name.id
            sql = '''
                   Select name as norm_name from mrp_bom where id = %s
                  '''%(norms[0])
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                 norm_name1 = move['norm_name']             
            return norm_name1 or ''
    
        def get_raw_mat(cb):
            raw = cb.product_id.id
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
        
        def get_leave_balance(cb):
            #wizard_data = self.localcontext['data']['form']
            date_from = cb.date_from
            date_to = cb.date_to      
            raw_mat=cb.product_id.id
            norms= cb.name.id
            res = []
            #date_from += datetime.timedelta(1)
            #datenext = wizard_data['date_from'] + 1
            
            if raw_mat:
                sql = '''
                           select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
                           a.sch_date as scheduled_date,a.app_qty as applied_qty
                           from (select p.default_code as material_code,p.name_template as material_name,
                           mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
                           from mrp_production_product_line mpp
                           join mrp_production mp on (mp.id = mpp.production_id)
                           join product_product p on (p.id = mpp.product_id) 
                           join mrp_bom bm on (bm.id = mp.bom_id)
                           join product_uom u on (u.id = mpp.product_uom)
                           where mp.date_planned between '%s' and '%s' 
                           and mp.bom_id = '%s' and p.id = '%s'and mp.state = 'done'
                           group by p.default_code,p.name_template,mp.date_planned,
                           u.name,mpp.product_qty
                           )a
                           order by a.material_code,a.sch_date
                            '''%(date_from,date_to,norms,raw_mat)
                cr.execute(sql)                    
                lst_val = []
                final_data = []
                count = 0
                for i in cr.dictfetchall():    
                    if i['mat_code'] in lst_val:
                        count += 1
                        val_str = 'applied_qty' + str(count)
                        data[val_str] = i['applied_qty']        
                    else:
                        data = {}
                        data.update(i)
                        lst_val.append(i['mat_code'])
                        count = 0
                    if not final_data:
                        final_data.append(data)
                    else:
                        l_data = len(final_data)
                        for pos, val in enumerate(final_data):
                            if val['mat_code'] == i['mat_code']:
                                del final_data[pos]
                                final_data.append(data)
                            else:
                                if pos == (l_data - 1):
                                    final_data.append(data)
                                else:
                                    continue
                for pos, val in enumerate(final_data):
                    for r in range(1,15):
                        m_str = 'applied_qty' + str(r)
                        if m_str not in val:
                            final_data[pos][m_str] = 0.0           
                return final_data
            
            else:
                sql = '''
                        select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
                           a.sch_date as scheduled_date,a.app_qty as applied_qty
                           from (select p.default_code as material_code,p.name_template as material_name,
                           mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
                           from mrp_production_product_line mpp
                           join mrp_production mp on (mp.id = mpp.production_id)
                           join product_product p on (p.id = mpp.product_id) 
                           join mrp_bom bm on (bm.id = mp.bom_id)
                           join product_uom u on (u.id = mpp.product_uom)
                           where mp.date_planned between '%s' and '%s' 
                           and mp.bom_id = '%s' and mp.state = 'done'
                           group by p.default_code,p.name_template,mp.date_planned,
                           u.name,mpp.product_qty
                           )a
                           order by a.material_code,a.sch_date
                            '''%(date_from,date_to,norms)
                cr.execute(sql)         
                lst_val = []
                final_data = []
                count = 0
                for i in cr.dictfetchall():    
                    if i['mat_code'] in lst_val:
                        count += 1
                        val_str = 'applied_qty' + str(count)
                        data[val_str] = i['applied_qty']        
                    else:
                        data = {}
                        data.update(i)
                        lst_val.append(i['mat_code'])
                        count = 0
                    if not final_data:
                        final_data.append(data)
                    else:
                        l_data = len(final_data)
                        for pos, val in enumerate(final_data):
                            if val['mat_code'] == i['mat_code']:
                                del final_data[pos]
                                final_data.append(data)
                            else:
                                if pos == (l_data - 1):
                                    final_data.append(data)
                                else:
                                    continue
                for pos, val in enumerate(final_data):
                    for r in range(1,15):
                        m_str = 'applied_qty' + str(r)
                        if m_str not in val:
                            final_data[pos][m_str] = 0.0           
                return final_data
        
        
        cr.execute('delete from daywise_consumption_report')
        cb_obj = self.pool.get('daywise.consumption.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        for line in get_leave_balance(cb):
            cb_line.append((0,0,{
                    'material_code':line['mat_code'],
                    'material_name':line['mat_name'],
                    'uom':line['uom'], 
                    'date_1':line['applied_qty'],
                    'date_2':line['applied_qty1'],
                    'date_3':line['applied_qty2'],
                    'date_4':line['applied_qty3'],
                    'date_5':line['applied_qty4'],
                    'date_6':line['applied_qty5'],
                    'date_7':line['applied_qty6'],
                    'date_8':line['applied_qty7'],
                    'date_9':line['applied_qty8'],
                    'date_10':line['applied_qty9'],
                    'date_11':line['applied_qty10'],      
                    'date_12':line['applied_qty11'],
                    'date_13':line['applied_qty12'],
                    'date_14':line['applied_qty13'],
                    'date_15':line['applied_qty14'],   
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
        
        
        
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'daywise.consumption.report'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'daywise_consumption_report', 'datas': datas}
        


day_wise_register()
