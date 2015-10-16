# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class mateiral_purchase_value_month(osv.osv_memory):
    _name = "mateiral.purchase.value.month"
    _columns = {
             'year': fields.many2one('account.fiscalyear','Year', required=True),
             'material_cate':fields.many2one('product.category','Material Category', required=True),
             'material_ids': fields.many2many('product.product', 'material_ref_report', 'mate_pur_month_id', 'product_id', 'Material'),  
             'avg_value': fields.selection(
            [('0', '0'),            
            ('1', '1 to 5000'),
            ('5001', '5001 to 10000'),
            ('all', 'All'),],
            'Average Value'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('review.mateiral.purchase.value.month')
        def get_category(o):
            cat = o.material_cate and o.material_cate.id or False
            if cat:
                cat_id = self.pool.get('product.category').browse(cr,uid,cat)
                if cat_id.cate_name == 'raw':
                    return "Raw Materials"
                if cat_id.cate_name == 'spares':
                    return "Spares"
                if cat_id.cate_name == 'finish':
                    return "Finished Product"
                if cat_id.cate_name == 'consum':
                    return "Consumables"
                if cat_id.cate_name == 'assets':
                    return "Assets"
                if cat_id.cate_name == 'service':
                    return "Services"
            return True
        
        def get_average(o):
            avg = o.avg_value or ''
            if avg:
                if avg == '0':
                    return "0"
                if avg == '1':
                    return "1 to 5000"
                if avg == '5001':
                    return "Finished 5001 to 10000"
                if avg == 'all':
                    return "All"
            return ''
        self.start = False
        self.stop = False
        def get_year(o):
            year = o.year and o.year.id or False
            if year:
                year_id = self.pool.get('account.fiscalyear').browse(cr,uid,year)
                cr.execute('''select EXTRACT(year from date_start) as start, EXTRACT(year from date_stop) as stop 
                                        from account_fiscalyear where id = %s''',(year,))
                date = cr.fetchone()
                self.start = date and date[0] or False
                self.stop = date and date[1] or False
                return year_id.name
            
        def get_material(o):
            product_ids = [r.id for r in o.material_ids]
            pro_name = ''
            if product_ids:
                for pro in product_ids:
                    product_id = self.pool.get('product.product').browse(cr,uid,pro)
                    pro_name += product_id.name + ','
                if pro_name != '':
                    pro_name = pro_name[:-1]
            return pro_name
        
        def get_line(o):
            cat = o.material_cate.id
            product_ids = [r.id for r in o.material_ids]
            avg_value = o.avg_value or ''
            if product_ids:
                product_ids = str(product_ids).replace("[","")
                product_ids = str(product_ids).replace("]","")
            else:
                product_ids = ''
            if avg_value:
                avg_value = avg_value
            else:
                avg_value=''
            return self.pool.get('sql.mateiral.purchase.value.month').get_line(cr, int(self.start), int(self.stop), cat, product_ids,avg_value)
        o = self.browse(cr, uid, ids[0])
        report_line = []
        vals = {
                'name': 'Material Purchase Value - Month Wise Report',
                'year': get_year(o),
                'material_cate':get_category(o),
                'material_ids': get_material(o),  
                'avg_value': get_average(o),
                }
        for line in get_line(o):
            report_line.append((0,0,{
                'product_name':line['product_name'],
                'product_code':line['product_code'],
                'm_4':line['m_4'],
                'm_5':line['m_5'],
                'm_6':line['m_6'],
                'm_7':line['m_7'],
                'm_8':line['m_8'],
                'm_9':line['m_9'],
                'm_10':line['m_10'],
                'm_11':line['m_11'],
                'm_12':line['m_12'],
                'm_1':line['m_1'],
                'm_2':line['m_2'],
                'm_3':line['m_3'],
                'avg':line['avg'],
                }))
        vals.update({'report_line':report_line})
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'review_mateiral_purchase_value_month_form')
        return {
                    'name': 'Material Purchase Value - Month Wise Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'review.mateiral.purchase.value.month',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                    'view_id': res and res[1] or False,
                }
        
mateiral_purchase_value_month()

class mateiral_purchase_value_day(osv.osv_memory):
    _name = "mateiral.purchase.value.day"
    _columns = {
             'year': fields.many2one('account.fiscalyear','Year'),
             'month_year': fields.many2one('account.period','Year and Month', required=True),
             'material_cate':fields.many2one('product.category','Material Category', required=True),
             'material_ids': fields.many2many('product.product', 'day_wise_material_ref_report', 'mate_pur_day_id', 'product_id', 'Material'),  
             'avg_value': fields.selection(
            [('0', '0'),            
            ('1', '1 to 5000'),
            ('5001', '5001 to 10000'),
            ('all', 'All'),],
            'Average Value'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('review.mateiral.purchase.value.day')
        def get_category(o):
            cat = o.material_cate and o.material_cate.id or False
            if cat:
                cat_id = self.pool.get('product.category').browse(cr,uid,cat)
                if cat_id.cate_name == 'raw':
                    return "Raw Materials"
                if cat_id.cate_name == 'spares':
                    return "Spares"
                if cat_id.cate_name == 'finish':
                    return "Finished Product"
                if cat_id.cate_name == 'consum':
                    return "Consumables"
                if cat_id.cate_name == 'assets':
                    return "Assets"
                if cat_id.cate_name == 'service':
                    return "Services"
            return True
        
        def get_average(o):
            avg = o.avg_value or ''
            if avg:
                if avg == '0':
                    return "0"
                if avg == '1':
                    return "1 to 5000"
                if avg == '5001':
                    return "Finished 5001 to 10000"
                if avg == 'all':
                    return "All"
            return ''
        self.year = False
        self.month = False
        def get_year(o):
            year = o.month_year and o.month_year.id or False
            if year:
                year_id = self.pool.get('account.period').browse(cr,uid,year)
                cr.execute('''select EXTRACT(year from date_start) as year, EXTRACT(month from date_start) as month 
                                        from account_period where id = %s''',(year,))
                date = cr.fetchone()
                self.year = date and int(date[0]) or False
                self.month = date and int(date[1]) or False
                return year_id.name
            
        def get_material(o):
            product_ids = [r.id for r in o.material_ids]
            pro_name = ''
            if product_ids:
                for pro in product_ids:
                    product_id = self.pool.get('product.product').browse(cr,uid,pro)
                    pro_name += product_id.name + ','
                if pro_name != '':
                    pro_name = pro_name[:-1]
            return pro_name
        
        def get_line(o):
            cat = o.material_cate.id
            product_ids = [r.id for r in o.material_ids]
            avg_value = o.avg_value or ''
            if product_ids:
                product_ids = str(product_ids).replace("[","")
                product_ids = str(product_ids).replace("]","")
            else:
                product_ids = ''
            if avg_value:
                avg_value = avg_value
            else:
                avg_value=''
            return self.pool.get('sql.mateiral.purchase.value.day').get_line(cr, int(self.year), int(self.month), cat, product_ids,avg_value)
        o = self.browse(cr, uid, ids[0])
        report_line = []
        vals = {
                'name': 'Material Purchase Value - Month Wise Report',
                'month_year': get_year(o),
                'material_cate':get_category(o),
                'material_ids': get_material(o),  
                'avg_value': get_average(o),
                }
        for line in get_line(o):
            report_line.append((0,0,{
                'product_name':line['product_name'],
                'product_code':line['product_code'],
                'm_1':line['m_1'],
                'm_2':line['m_2'],
                'm_3':line['m_3'],
                'm_4':line['m_4'],
                'm_5':line['m_5'],
                'm_6':line['m_6'],
                'm_7':line['m_7'],
                'm_8':line['m_8'],
                'm_9':line['m_9'],
                'm_10':line['m_10'],
                'm_11':line['m_11'],
                'm_12':line['m_12'],
                'm_13':line['m_13'],
                'm_14':line['m_14'],
                'm_15':line['m_15'],
                'm_16':line['m_16'],
                'm_17':line['m_17'],
                'm_18':line['m_18'],
                'm_19':line['m_19'],
                'm_20':line['m_20'],
                'm_21':line['m_21'],
                'm_22':line['m_22'],
                'm_23':line['m_23'],
                'm_24':line['m_24'],
                'm_25':line['m_25'],
                'm_26':line['m_26'],
                'm_27':line['m_27'],
                'm_28':line['m_28'],
                'm_29':line['m_29'],
                'm_30':line['m_30'],
                'm_31':line['m_31'],
                'avg':line['avg'],
                }))
        vals.update({'report_line':report_line})
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'review_mateiral_purchase_value_day_form')
        return {
                    'name': 'Material Purchase Value - Day Wise Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'review.mateiral.purchase.value.day',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                    'view_id': res and res[1] or False,
                }
        
mateiral_purchase_value_day()

class review_mateiral_purchase_value_month(osv.osv):
    _name = "review.mateiral.purchase.value.month"
    _columns = {
                'name':fields.char('Report', size=1024),
                 'year': fields.char('Year', size=1024),
                 'material_cate':fields.char('Material Category', size=1024),
                 'material_ids': fields.char('Material', size=1024),  
                 'avg_value': fields.char('Average Value', size=1024),
                 'report_line':fields.one2many('review.mateiral.purchase.value.month.line','master_id','Review'),
    }
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.mateiral.purchase.value.month'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_mateiral_purchase_value_month', 'datas': datas}   
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.mateiral.purchase.value.month'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_mateiral_purchase_value_month_pdf', 'datas': datas}   
     
review_mateiral_purchase_value_month()

class review_mateiral_purchase_value_month_line(osv.osv):
    _name = "review.mateiral.purchase.value.month.line"
    _columns = {
        'master_id':fields.many2one('review.mateiral.purchase.value.month','Report'),
        'product_name':fields.char('Material Name', size=1024),
        'product_code':fields.char('Material Code', size=1024),
        'm_4':fields.float('Apr'),
        'm_5':fields.float('May'),
        'm_6':fields.float('Jun'),
        'm_7':fields.float('Jul'),
        'm_8':fields.float('Aug'),
        'm_9':fields.float('Sep'),
        'm_10':fields.float('Oct'),
        'm_11':fields.float('Nov'),
        'm_12':fields.float('Dec'),
        'm_1':fields.float('Jan'),
        'm_2':fields.float('Feb'),
        'm_3':fields.float('Mar'),
        'avg':fields.float('Avg Value'),
                }
review_mateiral_purchase_value_month_line()

class review_mateiral_purchase_value_day(osv.osv):
    _name = "review.mateiral.purchase.value.day"
    _columns = {
                'name':fields.char('Report', size=1024),
                 'month_year': fields.char('Year and Month', size=1024),
                 'material_cate':fields.char('Material Category', size=1024),
                 'material_ids': fields.char('Material', size=1024),  
                 'avg_value': fields.char('Average Value', size=1024),
                 'report_line':fields.one2many('review.mateiral.purchase.value.day.line','master_id','Review'),
    }
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.mateiral.purchase.value.day'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'day_wise_report_material_purchase_value', 'datas': datas}   
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.mateiral.purchase.value.day'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'day_wise_report_material_purchase_value_pdf', 'datas': datas}   
     
review_mateiral_purchase_value_day()

class review_mateiral_purchase_value_day_line(osv.osv):
    _name = "review.mateiral.purchase.value.day.line"
    _columns = {
        'master_id':fields.many2one('review.mateiral.purchase.value.day','Report'),
        'product_name':fields.char('Material Name', size=1024),
        'product_code':fields.char('Material Code', size=1024),
        'm_1':fields.float('1'),
        'm_2':fields.float('2'),
        'm_3':fields.float('3'),
        'm_4':fields.float('4'),
        'm_5':fields.float('5'),
        'm_6':fields.float('6'),
        'm_7':fields.float('7'),
        'm_8':fields.float('8'),
        'm_9':fields.float('9'),
        'm_10':fields.float('10'),
        'm_11':fields.float('11'),
        'm_12':fields.float('12'),
        'm_13':fields.float('13'),
        'm_14':fields.float('14'),
        'm_15':fields.float('15'),
        'm_16':fields.float('16'),
        'm_17':fields.float('17'),
        'm_18':fields.float('18'),
        'm_19':fields.float('19'),
        'm_20':fields.float('20'),
        'm_21':fields.float('21'),
        'm_22':fields.float('22'),
        'm_23':fields.float('23'),
        'm_24':fields.float('24'),
        'm_25':fields.float('25'),
        'm_26':fields.float('26'),
        'm_27':fields.float('27'),
        'm_28':fields.float('28'),
        'm_29':fields.float('29'),
        'm_30':fields.float('30'),
        'm_31':fields.float('31'),
        'avg':fields.float('Avg Value'),
                }
review_mateiral_purchase_value_day_line()