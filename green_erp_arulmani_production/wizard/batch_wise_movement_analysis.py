# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import datetime
from datetime import date, datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class batch_wise_movement_analysis(osv.osv_memory):
    _name = "batch.wise.movement.analysis"
    _columns = {
            'production_date_from': fields.date('Production Date From:'),
            'production_date_to': fields.date('To:'),
            'batch_date_from': fields.date('Batch Date From:'),
            'batch_date_to': fields.date('To:'),
            'deliver_date_from': fields.date('Delivery Date From :'),
            'deliver_date_to': fields.date('To:'),
            'do_id': fields.many2one('stock.picking.out','DO Number'),
            'storage_from': fields.integer('Storage Days Range From :'),
            'storage_to': fields.integer('To:'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('review.batch.wise.movement.analysis')
        o = self.browse(cr, uid, ids[0])
        if not o.production_date_from and not o.batch_date_from and not o.deliver_date_from and not o.do_id and o.storage_from ==0 and o.storage_to == 0:
            raise osv.except_osv(_('Warning!'),_(' Please choose at least one condition to show report!'))    
        def get_date(date):
            if not date:
                date = time.strftime(DATE_FORMAT)
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
            
        def get_master(o):
            res = {}
            do_name = ''
            production_date_from = o.production_date_from or ''
            production_date_to = o.production_date_to or ''
            batch_date_from = o.batch_date_from or ''
            batch_date_to = o.batch_date_to or ''
            deliver_date_from = o.deliver_date_from or ''
            deliver_date_to = o.deliver_date_to or ''
            do_id = o.do_id and o.do_id.id or False
            storage_from = o.storage_from or 0
            storage_to = o.storage_to or 0
            if do_id:
                do_name = self.pool.get('stock.picking').browse(cr,uid,do_id).name
            res.update({'production_date_from': production_date_from and get_date(production_date_from) or '',
                        'production_date_to': production_date_to and get_date(production_date_to) or '',
                        'batch_date_from': batch_date_from and get_date(batch_date_from) or '',
                        'batch_date_to': batch_date_to and get_date(batch_date_to) or '',
                        'deliver_date_from': deliver_date_from and get_date(deliver_date_from) or '',
                        'deliver_date_to': deliver_date_to and get_date(deliver_date_to) or '',
                        'do_id': do_name,
                        'storage_from': storage_from,
                        'storage_to': storage_to,
                        })
            return res
        def get_line(o):
            res = []
            production_date_from = o.production_date_from and datetime.strptime(o.production_date_from, DATE_FORMAT) or ''
            production_date_to = o.production_date_to and datetime.strptime(o.production_date_to, DATE_FORMAT) or ''
            batch_date_from = o.batch_date_from and datetime.strptime(o.batch_date_from, DATE_FORMAT) or ''
            batch_date_to = o.batch_date_to and datetime.strptime(o.batch_date_to, DATE_FORMAT) or ''
            deliver_date_from = o.deliver_date_from and datetime.strptime(o.deliver_date_from, DATE_FORMAT) or ''
            deliver_date_to = o.deliver_date_to and datetime.strptime(o.deliver_date_to, DATE_FORMAT) or ''
            do_id = o.do_id and o.do_id.id or False
            storage_from = o.storage_from or 0
            storage_to = o.storage_to or 0
            sql = '''
                select id from tpt_batch_split_line where tio2_id in (select id from tpt_tio2_batch_split where state = 'confirm')
            '''
            
            if production_date_from and production_date_to:
                sql += '''and tio2_id in (select id from tpt_tio2_batch_split where mrp_id in (select id from mrp_production where date_planned between '%s' and '%s'))'''%(production_date_from,production_date_to)
            if batch_date_from and batch_date_to:
                sql += ''' and tio2_id in (select id from tpt_tio2_batch_split where name between '%s' and '%s') ''' %(batch_date_from,batch_date_to)
            if deliver_date_from and deliver_date_to:
                sql += ''' 
                    and prodlot_id in (select prodlot_id from stock_move where picking_id in 
                            (select id from stock_picking where type='out' and state='done' and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'))
                '''%(deliver_date_from,deliver_date_to)
            if do_id:
                sql = '''
                    select id from tpt_batch_split_line where tio2_id in (select id from tpt_tio2_batch_split where state = 'confirm')
                        and prodlot_id in (select prodlot_id from stock_move where picking_id = %s)
                '''%(do_id)
            
            cr.execute(sql)
            for r in cr.fetchall():
                split_id = self.pool.get('tpt.batch.split.line').browse(cr,uid,r[0])
                if split_id.prodlot_id and not do_id :
                    sql = '''
                        select id from stock_move where prodlot_id = %s and picking_id in (select id from stock_picking where type='out' and state='done')
                    '''%(split_id.prodlot_id.id)
                    cr.execute(sql)
                    move_ids = [l[0] for l in cr.fetchall()]
                    if move_ids:
                        for line in move_ids:
                            move_id = self.pool.get('stock.move').browse(cr,uid,line)
                            sql=''' select id from account_invoice where delivery_order_id = %s'''%(move_id.picking_id.id)
                            cr.execute(sql)
                            inv_ids = [i[0] for i in cr.fetchall()]
                            inv_num = ''
                            if inv_ids:
                                inv_id = self.pool.get('account.invoice').browse(cr,uid,inv_ids[0])
                                inv_num = inv_id.vvt_number and inv_id.vvt_number or ''
                            
                            days = (datetime.strptime(move_id.picking_id.date[:10], DATE_FORMAT)-datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days
                            if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                                res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                            'production_dec': split_id.tio2_id.mrp_id.name,
                                            'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                            'batch_no':split_id.prodlot_id.name,
                                            'delivery_date':get_date(move_id.picking_id.date[:10]),
                                            'do_number':move_id.picking_id.name,
                                            'deliver_qty':move_id.product_qty,
                                            'non_deliver_qty':split_id.prodlot_id.stock_available,
                                            'inv_num':inv_num,
                                            'store_days':days,
                                            })
                            if not storage_from and not storage_to:
                                res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                            'production_dec': split_id.tio2_id.mrp_id.name,
                                            'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                            'batch_no':split_id.prodlot_id.name,
                                            'delivery_date':get_date(move_id.picking_id.date[:10]),
                                            'do_number':move_id.picking_id.name,
                                            'deliver_qty':move_id.product_qty,
                                            'non_deliver_qty':split_id.prodlot_id.stock_available,
                                            'inv_num':inv_num,
                                            'store_days':days,
                                            })
                            if split_id.prodlot_id.stock_available != 0:
                                date_now = time.strftime('%Y-%m-%d')
                                days = (datetime.strptime(date_now, DATE_FORMAT) - datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days
                                if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                                    res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                            'production_dec': split_id.tio2_id.mrp_id.name,
                                            'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                            'batch_no':split_id.prodlot_id.name,
                                            'delivery_date':'',
                                            'do_number':'',
                                            'deliver_qty':0,
                                            'non_deliver_qty':split_id.prodlot_id.stock_available,
                                            'inv_num':'',
                                            'store_days':days,
                                            })
                                if not storage_from and not storage_to:
                                    res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                            'production_dec': split_id.tio2_id.mrp_id.name,
                                            'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                            'batch_no':split_id.prodlot_id.name,
                                            'delivery_date':'',
                                            'do_number':'',
                                            'deliver_qty':0,
                                            'non_deliver_qty':split_id.prodlot_id.stock_available,
                                            'inv_num':'',
                                            'store_days':days,
                                            })
                    else:
                        date_now = time.strftime('%Y-%m-%d')
                        days = (datetime.strptime(date_now, DATE_FORMAT) - datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days
                        if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                            res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                    'production_dec': split_id.tio2_id.mrp_id.name,
                                    'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                    'batch_no':split_id.prodlot_id.name,
                                    'delivery_date':'',
                                    'do_number':'',
                                    'deliver_qty':0,
                                    'non_deliver_qty':split_id.prodlot_id.stock_available,
                                    'inv_num':'',
                                    'store_days':days,
                                    })
                        if not storage_from and not storage_to:
                            res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                    'production_dec': split_id.tio2_id.mrp_id.name,
                                    'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                    'batch_no':split_id.prodlot_id.name,
                                    'delivery_date':'',
                                    'do_number':'',
                                    'deliver_qty':0,
                                    'non_deliver_qty':split_id.prodlot_id.stock_available,
                                    'inv_num':'',
                                    'store_days':days,
                                    })
                if do_id and split_id.prodlot_id:
                    sql = '''
                        select id from stock_move where picking_id = %s and prodlot_id = %s
                    '''%(do_id,split_id.prodlot_id.id)
                    cr.execute(sql)
                    move_ids = [l[0] for l in cr.fetchall()]
                    for line in move_ids:
                        move_id = self.pool.get('stock.move').browse(cr,uid,line)
                        sql=''' select id from account_invoice where delivery_order_id = %s'''%(move_id.picking_id.id)
                        cr.execute(sql)
                        inv_ids = [i[0] for i in cr.fetchall()]
                        inv_num = ''
                        if inv_ids:
                            inv_id = self.pool.get('account.invoice').browse(cr,uid,inv_ids[0])
                            inv_num = inv_id.vvt_number and inv_id.vvt_number or ''
                            
                        days = (datetime.strptime(move_id.picking_id.date[:10], DATE_FORMAT) - datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days 
                        if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                            res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                        'batch_no':split_id.prodlot_id.name,
                                        'delivery_date':get_date(move_id.picking_id.date[:10]),
                                        'do_number':move_id.picking_id.name,
                                        'deliver_qty':move_id.product_qty,
                                        'non_deliver_qty':split_id.prodlot_id.stock_available,
                                        'inv_num':inv_num,
                                        'store_days':days,
                                        })
                        if not storage_from and not storage_to:
                            res.append({'production_date': get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':get_date(split_id.prodlot_id.date[:10]),
                                        'batch_no':split_id.prodlot_id.name,
                                        'delivery_date':get_date(move_id.picking_id.date[:10]),
                                        'do_number':move_id.picking_id.name,
                                        'deliver_qty':move_id.product_qty,
                                        'non_deliver_qty':split_id.prodlot_id.stock_available,
                                        'inv_num':inv_num,
                                        'store_days':days,
                                        })
            return res
        report_line = []
        vals = {
                'name': 'Batch Wise Movement Analysis Report',
                'production_date_from': get_master(o)['production_date_from'],
                'production_date_to': get_master(o)['production_date_to'],
                'batch_date_from': get_master(o)['batch_date_from'],
                'batch_date_to': get_master(o)['batch_date_to'],
                'deliver_date_from': get_master(o)['deliver_date_from'],
                'deliver_date_to': get_master(o)['deliver_date_to'],
                'do_id': get_master(o)['do_id'],
                'storage_from': get_master(o)['storage_from'],
                'storage_to': get_master(o)['storage_to'],
                }
        for line in get_line(o):
            report_line.append((0,0,{
                'production_date': line['production_date'],
                'production_dec': line['production_dec'],
                'batch_date':line['batch_date'],
                'batch_no':line['batch_no'],
                'delivery_date':line['delivery_date'],
                'do_number':line['do_number'],
                'deliver_qty':line['deliver_qty'],
                'non_deliver_qty':line['non_deliver_qty'],
                'inv_num':line['inv_num'],
                'store_days':line['store_days'],
                }))
        vals.update({'report_line':report_line})
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_production', 'review_batch_wise_movement_analysis_form')
        return {
                    'name': 'Batch Wise Movement Analysis Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'review.batch.wise.movement.analysis',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                    'view_id': res and res[1] or False,
                }
        
     

batch_wise_movement_analysis()

class review_batch_wise_movement_analysis(osv.osv):
    _name = "review.batch.wise.movement.analysis"
    _columns = {
                'name': fields.char('Name:', size=1024),
                 'production_date_from': fields.char('Production Date From:', size=1024),
                'production_date_to': fields.char('To:', size=1024),
                'batch_date_from': fields.char('Batch Date From:', size=1024),
                'batch_date_to': fields.char('To:', size=1024),
                'deliver_date_from': fields.char('Delivery Date From :', size=1024),
                'deliver_date_to': fields.char('To:', size=1024),
                'do_id': fields.char('DO Number', size=1024),
                'storage_from': fields.integer('Storage Days Range From :'),
                'storage_to': fields.integer('To:'),
                 'report_line':fields.one2many('review.batch.wise.movement.analysis.line','master_id','Review'),
    }
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.batch.wise.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_batch_wise_movement_analysis', 'datas': datas}   
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'review.batch.wise.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_batch_wise_movement_analysis_pdf', 'datas': datas}   
     
review_batch_wise_movement_analysis()

class review_batch_wise_movement_analysis_line(osv.osv):
    _name = "review.batch.wise.movement.analysis.line"
    _columns = {
        'master_id':fields.many2one('review.batch.wise.movement.analysis','Report'),
        'production_date': fields.char('Production Date', size=1024),
        'production_dec': fields.char('Production Dec No', size=1024),
        'batch_date':fields.char('Batch Date', size=1024),
        'batch_no':fields.char('Batch No', size=1024),
        'delivery_date':fields.char('Delivery Date', size=1024),
        'do_number':fields.char('DO Number', size=1024),
        'deliver_qty':fields.float('Delivery Qty'),
        'non_deliver_qty':fields.float('Non - Delivered Qty'),
        'inv_num':fields.char('Invoice Number', size=1024),
        'store_days':fields.float('Storage Days'),
                }
review_batch_wise_movement_analysis_line()
