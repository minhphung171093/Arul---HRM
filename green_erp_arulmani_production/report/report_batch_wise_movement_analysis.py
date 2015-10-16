# -*- coding: utf-8 -*-
##############################################################################
#
#    Tenth Planet Technologies
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
from green_erp_arulmani_purchase.report.amount_to_text_indian import Number2Words
import random
import datetime
from datetime import date, datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from green_erp_arulmani_purchase.report import amount_to_text_en

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.start = False
        self.stop = False
        self.localcontext.update({
            'get_line':self.get_line, 
            'get_date':self.get_date, 
            'get_master': self.get_master,
        })
        
    def get_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
        
    def get_master(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        production_date_from = wizard_data['production_date_from'] or ''
        production_date_to = wizard_data['production_date_to'] or ''
        batch_date_from = wizard_data['batch_date_from'] or ''
        batch_date_to = wizard_data['batch_date_to'] or ''
        deliver_date_from = wizard_data['deliver_date_from'] or ''
        deliver_date_to = wizard_data['deliver_date_to'] or ''
        do_id = wizard_data['do_id'] and wizard_data['do_id'][0] or ''
        storage_from = wizard_data['storage_from'] or 0
        storage_to = wizard_data['storage_to'] or 0
        res.update({'production_date_from': production_date_from and self.get_date(production_date_from) or '',
                    'production_date_to': production_date_to and self.get_date(production_date_to) or '',
                    'batch_date_from': batch_date_from and self.get_date(batch_date_from) or '',
                    'batch_date_to': batch_date_to and self.get_date(batch_date_to) or '',
                    'deliver_date_from': deliver_date_from and self.get_date(deliver_date_from) or '',
                    'deliver_date_to': deliver_date_to and self.get_date(deliver_date_to) or '',
                    'do_id': do_id,
                    'storage_from': storage_from,
                    'storage_to': storage_to,
                    })
        return res
    def get_line(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        production_date_from = wizard_data['production_date_from'] and datetime.strptime(wizard_data['production_date_from'], DATE_FORMAT) or ''
        production_date_to = wizard_data['production_date_to'] and datetime.strptime(wizard_data['production_date_to'], DATE_FORMAT) or ''
        batch_date_from = wizard_data['batch_date_from'] and datetime.strptime(wizard_data['batch_date_from'], DATE_FORMAT) or ''
        batch_date_to = wizard_data['batch_date_to'] and datetime.strptime(wizard_data['batch_date_to'], DATE_FORMAT) or ''
        deliver_date_from = wizard_data['deliver_date_from'] and datetime.strptime(wizard_data['deliver_date_from'], DATE_FORMAT) or ''
        deliver_date_to = wizard_data['deliver_date_to'] and datetime.strptime(wizard_data['deliver_date_to'], DATE_FORMAT) or ''
        do_id = wizard_data['do_id'] and wizard_data['do_id'][0] or False
        storage_from = wizard_data['storage_from'] or 0
        storage_to = wizard_data['storage_to'] or 0
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
        
        self.cr.execute(sql)
        for r in self.cr.fetchall():
            split_id = self.pool.get('tpt.batch.split.line').browse(self.cr,self.uid,r[0])
            if split_id.prodlot_id and not do_id :
                sql = '''
                    select id from stock_move where prodlot_id = %s and picking_id in (select id from stock_picking where type='out' and state='done')
                '''%(split_id.prodlot_id.id)
                self.cr.execute(sql)
                move_ids = [l[0] for l in self.cr.fetchall()]
                if move_ids:
                    for line in move_ids:
                        move_id = self.pool.get('stock.move').browse(self.cr,self.uid,line)
                        sql=''' select id from account_invoice where delivery_order_id = %s'''%(move_id.picking_id.id)
                        self.cr.execute(sql)
                        inv_ids = [i[0] for i in self.cr.fetchall()]
                        inv_num = ''
                        if inv_ids:
                            inv_id = self.pool.get('account.invoice').browse(self.cr,self.uid,inv_ids[0])
                            inv_num = inv_id.vvt_number and inv_id.vvt_number or ''
                        
                        days = (datetime.strptime(move_id.picking_id.date[:10], DATE_FORMAT)-datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days
                        if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                            res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                        'batch_no':split_id.prodlot_id.name,
                                        'delivery_date':self.get_date(move_id.picking_id.date[:10]),
                                        'do_number':move_id.picking_id.name,
                                        'deliver_qty':move_id.product_qty,
                                        'non_deliver_qty':split_id.prodlot_id.stock_available,
                                        'inv_num':inv_num,
                                        'store_days':days,
                                        })
                        if not storage_from and not storage_to:
                            res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                        'batch_no':split_id.prodlot_id.name,
                                        'delivery_date':self.get_date(move_id.picking_id.date[:10]),
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
                                res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                        'batch_no':split_id.prodlot_id.name,
                                        'delivery_date':'',
                                        'do_number':'',
                                        'deliver_qty':0,
                                        'non_deliver_qty':split_id.prodlot_id.stock_available,
                                        'inv_num':'',
                                        'store_days':days,
                                        })
                            if not storage_from and not storage_to:
                                res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                        'production_dec': split_id.tio2_id.mrp_id.name,
                                        'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
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
                        res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                'production_dec': split_id.tio2_id.mrp_id.name,
                                'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                'batch_no':split_id.prodlot_id.name,
                                'delivery_date':'',
                                'do_number':'',
                                'deliver_qty':0,
                                'non_deliver_qty':split_id.prodlot_id.stock_available,
                                'inv_num':'',
                                'store_days':days,
                                })
                    if not storage_from and not storage_to:
                        res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                'production_dec': split_id.tio2_id.mrp_id.name,
                                'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
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
                self.cr.execute(sql)
                move_ids = [l[0] for l in self.cr.fetchall()]
                for line in move_ids:
                    move_id = self.pool.get('stock.move').browse(self.cr,self.uid,line)
                    sql=''' select id from account_invoice where delivery_order_id = %s'''%(move_id.picking_id.id)
                    self.cr.execute(sql)
                    inv_ids = [i[0] for i in self.cr.fetchall()]
                    inv_num = ''
                    if inv_ids:
                        inv_id = self.pool.get('account.invoice').browse(self.cr,self.uid,inv_ids[0])
                        inv_num = inv_id.vvt_number and inv_id.vvt_number or ''
                        
                    days = (datetime.strptime(move_id.picking_id.date[:10], DATE_FORMAT) - datetime.strptime(split_id.prodlot_id.date[:10], DATE_FORMAT)).days 
                    if (storage_from != 0 or storage_to != 0) and days>=storage_from and days<=storage_to:
                        res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                    'production_dec': split_id.tio2_id.mrp_id.name,
                                    'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                    'batch_no':split_id.prodlot_id.name,
                                    'delivery_date':self.get_date(move_id.picking_id.date[:10]),
                                    'do_number':move_id.picking_id.name,
                                    'deliver_qty':move_id.product_qty,
                                    'non_deliver_qty':split_id.prodlot_id.stock_available,
                                    'inv_num':inv_num,
                                    'store_days':days,
                                    })
                    if not storage_from and not storage_to:
                        res.append({'production_date': self.get_date(split_id.tio2_id.mrp_id.date_planned),
                                    'production_dec': split_id.tio2_id.mrp_id.name,
                                    'batch_date':self.get_date(split_id.prodlot_id.date[:10]),
                                    'batch_no':split_id.prodlot_id.name,
                                    'delivery_date':self.get_date(move_id.picking_id.date[:10]),
                                    'do_number':move_id.picking_id.name,
                                    'deliver_qty':move_id.product_qty,
                                    'non_deliver_qty':split_id.prodlot_id.stock_available,
                                    'inv_num':inv_num,
                                    'store_days':days,
                                    })
        return res
