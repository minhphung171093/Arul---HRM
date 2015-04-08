# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class tpt_tio2_batch_split(osv.osv):
    _name = 'tpt.tio2.batch.split'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'name': fields.date('Created Date', states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'mrp_id': fields.many2one('mrp.production', 'Production Decl. No', required=True, states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'location_id': fields.many2one('stock.location', 'Warehouse Location', required=True, states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'available': fields.related('mrp_id', 'product_qty',string='Available Stock',store=True,readonly=True),
        'stating_batch_no': fields.char('Stating Batch No', size=100,readonly=True, states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'batch_split_line': fields.one2many('tpt.batch.split.line', 'tio2_id', 'Batch Split Line', states={'generate': [('readonly', True)], 'confirm':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('generate', 'Generated'),('confirm', 'Confirm')],'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'name': time.strftime('%Y-%m-%d'),
        'stating_batch_no': '/',
    }
    
    def bt_generate(self, cr, uid, ids, context=None):
        batch_split_line_obj = self.pool.get('tpt.batch.split.line')
        prodlot_obj = self.pool.get('stock.production.lot')
        for line in self.browse(cr, uid, ids):
            schedule_date = line.mrp_id.date_planned
            schedule_date_day = schedule_date[8:10]
            schedule_date_month = schedule_date[5:7]
            schedule_date_year = schedule_date[:4]
            prefix = ''
            if line.product_id.name in ('TITANIUM DIOXIDE-RUTILE','M0501010008') or line.product_id.default_code in ('TITANIUM DIOXIDE-RUTILE','M0501010008'):
                prefix = 'R'
            if line.product_id.name in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001') or line.product_id.default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'):
                prefix = 'A'
            for num in range(0,int(line.available)):
                prodlot = self.pool.get('ir.sequence').get(cr, uid, 'batching.tio2')
                prodlot_name = prefix + str(schedule_date_year) + str(schedule_date_month) + str(schedule_date_day) + str(prodlot)
                prodlot_id = prodlot_obj.create(cr, uid, {'name': prodlot_name,
                                            'phy_batch_no': prodlot_name,
                                             'product_id': line.product_id.id,
                                             'location_id': line.location_id.id})
                batch_split_line_obj.create(cr, uid, {
                                    'tio2_id': line.id,
                                    'sequence': num+1,
                                    'product_id': line.product_id.id,
                                    'qty': 1.0,
                                    'uom_id': line.product_id.uom_id.id,
                                    'prodlot_id': prodlot_id,
                                                      })
            self.write(cr, uid, [line.id],{'state':'generate'})
        return True
    
    def bt_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_split_obj = self.pool.get('stock.move.split')
        move_obj = self.pool.get('stock.move')
        for line in self.browse(cr, uid, ids):
            move_ids = move_obj.search(cr, uid, [('scrapped','=',False),('production_id','=',line.mrp_id.id),('product_id','=',line.product_id.id)])
            cr.execute('update stock_move set location_dest_id=%s where id in %s',(line.location_id.id,tuple(move_ids),))
#             move_obj.write(cr, uid, move_ids,{'location_dest_id':line.location_id.id})
            context.update({'active_id': move_ids and move_ids[0] or False,'active_model': 'stock.move','tpt_copy_prodlot':True})
            line_exist_ids = []
            for split_line in line.batch_split_line:
                self.pool.get('tpt.quality.verification').create(cr,uid,{
                                                                  'prod_batch_id': split_line.prodlot_id and split_line.prodlot_id.id or False,
                                                                  'phy_batch_no': split_line.prodlot_id and split_line.prodlot_id.phy_batch_no or False,
                                                                  'product_id': split_line.product_id and split_line.product_id.id or False,
                                                                  'warehouse_id': line.location_id and line.location_id.id or False,
                                                                  })
                line_exist_ids.append((0,0,{
                    'quantity': split_line.qty,
                    'prodlot_id': split_line.prodlot_id.id,
                                       }))
            vals = {
                'use_exist': True,
                'line_exist_ids': line_exist_ids,
            }
            move_split_id = move_split_obj.create(cr, uid, vals, context)
            res = move_split_obj.split(cr, uid, [move_split_id],[move_ids and move_ids[0] or []],context)
        return self.write(cr, uid, ids,{'state':'confirm'})
    
    def onchange_mrp_id(self, cr, uid, ids, mrp_id, context=None):
        if mrp_id:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
            v = {'available': mrp.product_qty,'location_id': mrp.location_dest_id.id}
            return {'value': v}
        return {}
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('stating_batch_no','/')=='/':
            
            company_ids = self.pool.get('res.company').search(cr, uid, [], context=context) + [False]
            seq_ids = self.pool.get('ir.sequence').search(cr, uid, ['&', ('code', '=', 'batching.tio2'), ('company_id', 'in', company_ids)])
            
            force_company = context.get('force_company')
            if not force_company:
                force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            sequences = self.pool.get('ir.sequence').read(cr, uid, seq_ids, ['name','company_id','implementation','number_next','prefix','suffix','padding', 'number_increment', 'auto_reset', 'reset_period', 'reset_time', 'reset_init_number'])
            preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company ]
            seq = preferred_sequences[0] if preferred_sequences else sequences[0]
            if seq['implementation'] == 'standard':
                current_time =':'.join([seq['reset_period'], self.pool.get('ir.sequence')._interpolation_dict().get(seq['reset_period'])])
                if seq['auto_reset'] and current_time != seq['reset_time']:
                    cr.execute("UPDATE ir_sequence SET reset_time=%s WHERE id=%s ", (current_time,seq['id']))
                    self.pool.get('ir.sequence')._alter_sequence(cr, seq['id'], seq['number_increment'], seq['reset_init_number'])
                    cr.commit()
                temp = 0
                try:
                    cr.execute("SELECT setval('ir_sequence_%03d',nextval('ir_sequence_%03d')-1)+1" % (seq['id'],seq['id']))
                    seq['number_next'] = cr.fetchone()
                except Exception, e:
                    cr.rollback()
                    temp = 1
                    pass
                if temp==1:
                    self.pool.get('ir.sequence')._alter_sequence(cr, seq['id'], seq['number_increment'], seq['reset_init_number'])
                    seq['number_next'] = 1
            else:
                cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
            d = self.pool.get('ir.sequence')._interpolation_dict()
            try:
                interpolated_prefix = self.pool.get('ir.sequence')._interpolate(seq['prefix'], d)
                interpolated_suffix = self.pool.get('ir.sequence')._interpolate(seq['suffix'], d)
            except ValueError:
                raise osv.except_osv(_('Warning'), _('Invalid prefix or suffix for sequence \'%s\'') % (seq.get('name')))
            sequence = interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix
            cr.execute("UPDATE ir_sequence SET number_next=number_next-number_increment WHERE id=%s ", (seq['id'],))
            
            line = self.pool.get('mrp.production').browse(cr, uid, vals['mrp_id'])
            schedule_date = line.date_planned
            schedule_date_day = schedule_date[8:10]
            schedule_date_month = schedule_date[5:7]
            schedule_date_year = schedule_date[:4]
            prefix = ''
            if line.product_id.name in ('TITANIUM DIOXIDE-RUTILE','M0501010008') or line.product_id.default_code in ('TITANIUM DIOXIDE-RUTILE','M0501010008'):
                prefix = 'R'
            if line.product_id.name in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001') or line.product_id.default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'):
                prefix = 'A'
            prodlot_name = prefix + str(schedule_date_year) + str(schedule_date_month) + str(schedule_date_day) + str(sequence)
            vals['stating_batch_no'] = prodlot_name or '/'
        new_id = super(tpt_tio2_batch_split, self).create(cr, uid, vals, context=context)
        return new_id
    
    def unlink(self, cr, uid, ids, context=None):
        leave_details = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for ld in leave_details:
            if ld['state'] in ['draft']:
                unlink_ids.append(ld['id'])
            else:
                raise osv.except_osv(_('Warning!'), _('Can not delete this Batch Split after it was generated!'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
tpt_tio2_batch_split()

class tpt_batch_split_line(osv.osv):
    _name = 'tpt.batch.split.line'
    _columns = {
        'tio2_id': fields.many2one('tpt.tio2.batch.split', 'Tio2 Batch Split', ondelete='cascade'),
        'sequence': fields.integer('S.No'),
        'product_id': fields.many2one('product.product', 'Product'),
        'qty': fields.float('Quantity'),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'prodlot_id': fields.many2one('stock.production.lot', 'System Batch No'),
    }
    _defaults = {
    }
    
tpt_batch_split_line()


class tpt_fsh_batch_split(osv.osv):
    _name = 'tpt.fsh.batch.split'
    
#     def _get_available(self, cr, uid, ids, name, arg, context=None):
#         res = {}
#         for line in self.browse(cr, uid, ids):
#             available = 0.0
#             if line.mrp_id.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or line.mrp_id.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
#                 sql = '''
#                         select id from stock_production_lot where name='temp_fsh'
#                     '''
#                 cr.execute(sql)
#                 prodlot_ids = cr.fetchone()
#                 if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<line.mrp_id.product_qty:
#                     available = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available
#                 else:
#                     available = line.mrp_id.product_qty
#             res[line.id] = available
#         return res
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'name': fields.date('Created Date'),
        'mrp_id': fields.many2one('mrp.production', 'Production Decl. No', required=True),
        'location_id': fields.many2one('stock.location', 'Warehouse Location', required=True),
        'available': fields.float('Available Stock', readonly=True),
        'batchable_qty': fields.float('Batchable Quantity'),
        'batch_split_line': fields.one2many('tpt.fsh.batch.split.line', 'fsh_id', 'Batch Split Line'),
        'state':fields.selection([('draft', 'Draft'),('confirm', 'Confirm')],'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'name': time.strftime('%Y-%m-%d'),
    }
    
    def _check_batchable_qty(self, cr, uid, ids, context=None):
        for quantity in self.browse(cr, uid, ids, context=context):
            amount = 0
            if quantity.batchable_qty > quantity.available:
                raise osv.except_osv(_('Warning!'),_('Batchable Quantity is not more than Available Stock Quantity !'))
                return False
            for line in quantity.batch_split_line:
                amount += line.qty
                if (amount > quantity.batchable_qty):
                    raise osv.except_osv(_('Warning!'),_('The total Quantity for each line is not more than Batchable Quantity !'))
                    return False
            return True
        
    _constraints = [
        (_check_batchable_qty, 'Identical Data', []),
    ]       
    
    def bt_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_split_obj = self.pool.get('stock.move.split')
        move_obj = self.pool.get('stock.move')
        for line in self.browse(cr, uid, ids):
            
            available = 0.0
            if line.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or line.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
                sql = '''
                        select id from stock_production_lot where name='temp_fsh'
                    '''
                cr.execute(sql)
                prodlot_ids = cr.fetchone()
                if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<line.available:
                    raise osv.except_osv(_('Warning!'),_('Batchable Quantity is not more than Available Stock Quantity !'))
            move_ids = move_obj.search(cr, uid, [('scrapped','=',False),('production_id','=',line.mrp_id.id),('product_id','=',line.product_id.id)])
            cr.execute('update stock_move set location_dest_id=%s where id in %s',(line.location_id.id,tuple(move_ids),))
#             move_obj.write(cr, uid, move_ids,{'location_dest_id':line.location_id.id})
            context.update({'active_id': move_ids and move_ids[0] or False,'active_model': 'stock.move','tpt_copy_prodlot':True})
            line_exist_ids = []
            for split_line in line.batch_split_line:
                line_exist_ids.append((0,0,{
                    'quantity': split_line.qty,
                    'prodlot_id': split_line.prodlot_id.id,
                                       }))
            vals = {
                'use_exist': True,
                'line_exist_ids': line_exist_ids,
            }
            move_split_id = move_split_obj.create(cr, uid, vals, context)
            res = move_split_obj.split(cr, uid, [move_split_id],[move_ids and move_ids[0] or []],context)
        return self.write(cr, uid, ids,{'state':'confirm'})
    
    def onchange_mrp_id(self, cr, uid, ids, mrp_id, context=None):
        if mrp_id:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
            available = 0.0
            batchable = 0.0
            if mrp.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or mrp.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
                sql = '''
                        select id from stock_production_lot where name='temp_fsh'
                    '''
                cr.execute(sql)
                prodlot_ids = cr.fetchone()
                if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<mrp.product_qty:
                    available = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available
                else:
                    available = mrp.product_qty
                batchable = available
            v = {'available': available,'batchable_qty': batchable, 'location_id': mrp.location_dest_id.id}
            return {'value': v}
        return {}
    
    def create(self, cr, uid, vals, context=None):
        if 'mrp_id' in vals:
            mrp = self.pool.get('mrp.production').browse(cr, uid, vals['mrp_id'], context=context)
            available = 0.0
            if mrp.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or mrp.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
                sql = '''
                        select id from stock_production_lot where name='temp_fsh'
                    '''
                cr.execute(sql)
                prodlot_ids = cr.fetchone()
                if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<mrp.product_qty:
                    available = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available
                else:
                    available = mrp.product_qty
            vals.update({'available':available})
        new_id = super(tpt_fsh_batch_split, self).create(cr, uid, vals, context=context)
#         new = self.browse(cr, uid, new_id)
#         sum = 0
#         for line in new.batch_split_line:
#             sum+=line.qty
#         if sum!=new.available:
#             raise osv.except_osv(_('Warning!'),_('The sum of Qtys entered in the Batch split should match with the available stock quantity entered at the header'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
#         for mrp in self.browse(cr, uid, ids):
#             available = 0.0
#             if mrp.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or mrp.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
#                 sql = '''
#                         select id from stock_production_lot where name='temp_fsh'
#                     '''
#                 cr.execute(sql)
#                 prodlot_ids = cr.fetchone()
#                 if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<mrp.mrp_id.product_qty:
#                     available = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available
#                 else:
#                     available = mrp.mrp_id.product_qty
#             vals.update({'available':available})
        new_write = super(tpt_fsh_batch_split, self).write(cr, uid,ids, vals, context)
#         for new in self.browse(cr, uid, ids):
#             sum = 0
#             for line in new.batch_split_line:
#                 sum+=line.qty
#             if sum!=new.available:
#                 raise osv.except_osv(_('Warning!'),_('The sum of Qtys entered in the Batch split should match with the available stock quantity entered at the header'))
        return new_write
    
tpt_fsh_batch_split()

class tpt_fsh_batch_split_line(osv.osv):
    _name = 'tpt.fsh.batch.split.line'
    _columns = {
        'fsh_id': fields.many2one('tpt.fsh.batch.split', 'FSH Batch Split', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'qty': fields.float('Quantity',required=True),
        'uom_id': fields.many2one('product.uom', 'UOM', required=True,readonly=True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Batch Type',required=True),
    }
    _defaults = {
        'qty': 1.0,
    }
    def _check_prodlot_id(self, cr, uid, ids, context=None):
        for prodlot in self.browse(cr, uid, ids, context=context):
            prodlot_ids = self.search(cr, uid, [('id','!=',prodlot.id),('prodlot_id','=',prodlot.prodlot_id.id),('fsh_id','=',prodlot.fsh_id.id)])
            if prodlot_ids:
                raise osv.except_osv(_('Warning!'),_('Batch Type is not duplicate !'))
                return False
            return True
        
    _constraints = [
        (_check_prodlot_id, 'Identical Data', ['prodlot_id', 'fsh_id']),
    ]       
    def create(self, cr, uid, vals, context=None):
        
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_id':product.uom_id.id})
        new_id = super(tpt_fsh_batch_split_line, self).create(cr, uid, vals, context)
        return new_id    
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            return {'value': {'uom_id': prod.uom_id.id}}
        return {}
    
tpt_fsh_batch_split_line()

class tpt_activities(osv.osv):
    _name = "tpt.activities"
    _order = "code"
    _columns = {
                
        'name': fields.char('Name', size = 1024, required=True),
        'code':fields.char('Code',size = 256,required = True),
        'uom_po_id': fields.many2one('product.uom','UOM',required = True), 
        'description':fields.text('Description'),
                }
    
    _defaults = {
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_activities, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_activities, self).write(cr, uid,ids, vals, context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['code'], context)
  
        for record in reads:
            code = record['code']
            res.append((record['id'], code))
        return res 


    def _check_code_id(self, cr, uid, ids, context=None):
        for vendor in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_activities where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(vendor.id,vendor.code,vendor.name)
            cr.execute(sql)
            vendor_ids = [row[0] for row in cr.fetchall()]
            if vendor_ids:  
                raise osv.except_osv(_('Warning!'),_('Name or Code in Vendor Group should be unique!'))
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
    
tpt_activities()

class crm_application(osv.osv):
    _inherit = 'crm.application'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',required=False),
        'application_line': fields.one2many('crm.application.line', 'application_id', 'Application Line'),
    }
    _defaults = {
    }
    
    def _check_product_id(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            product_ids = self.search(cr, uid, [('id','!=',product.id),('product_id','=',product.product_id.id)])
            if product_ids:
                raise osv.except_osv(_('Warning!'),_('Different Products are not allowed in same Application Master!'))           
                return False
            return True
        
    _constraints = [
        #TPT-Commented By BalamuruganPurushothaman - ON 17/03/2015 - TO AVOID CHECKING THIS CONSTRAINS
        #(_check_product_id, 'Identical Data', ['product_id']),
    ]       
    
crm_application()

class crm_application_line(osv.osv):
    _name = 'crm.application.line'
    _columns = {
        'application_id': fields.many2one('crm.application', 'Application', ondelete='cascade'),
        'parameters_id': fields.many2one('tpt.quality.parameters', 'Parameters', required=True),
        'standard_value':fields.char('Standard Value',size = 256),
        'exp_value':fields.char('Experiment Value',size = 256),
        'batch_verifi_id': fields.many2one('tpt.quality.verification','Batch Quality',ondelete='cascade'),
    }
    _defaults = {
    }
    
crm_application_line()

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def _norms(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for master in self.browse(cr,uid,ids,context=context):
            res[master.id] = {
                    'product_cost': 0.0
                } 
            res[master.id]['product_cost'] = master.product_qty * master.price_unit
            if master.cost_type == 'variable' :
                res[master.id]['product_cost'] = master.product_qty * master.price_unit
#                 sql='''
#                     select product_id, sum(product_qty) as product_qty, sum(line_net) as line_net from purchase_order_line where product_id = %s group by product_id
#                 '''%(master.product_id.id)
#                 cr.execute(sql)
#                 for product in cr.dictfetchall():
#                     res[master.id]['product_cost'] = product['line_net']/product['product_qty']
            if master.cost_type == 'fixed':
                res[master.id]['product_cost'] = master.product_qty * master.price_unit
        return res
    
    def sum_finish_function(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for master in self.browse(cr,uid,ids,context=context):
            product_cost = 0.0
            product_cost_acti=0.0
            sql='''
                    select case when sum(product_cost)!=0 then sum(product_cost) else 0 end product_cost from mrp_bom where bom_id = %s
                '''%(master.id)
            cr.execute(sql)
            product_cost = cr.dictfetchone()['product_cost']
            sql='''
                    select case when sum(product_cost)!=0 then sum(product_cost) else 0 end product_cost_acti from tpt_activities_line where bom_id = %s
                '''%(master.id)
            cr.execute(sql)
            product_cost_acti = cr.dictfetchone()['product_cost_acti']
            result = product_cost + product_cost_acti
            res[master.id] = result
        return res
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'date_start': fields.date('Valid From', help="Validity of this BoM or component. Keep empty if it's always valid.", states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'date_stop': fields.date('Valid Until', help="Validity of this BoM or component. Keep empty if it's always valid.", states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'product_qty': fields.float('Product Quantity', required=True, digits_compute=dp.get_precision('Product Unit of Measure'), states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the bills of material without removing it."),
        'name': fields.text('Name', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'code': fields.char('Reference', size=16, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'company_id': fields.many2one('res.company','Company',required=True, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'cost_type': fields.selection([('variable','Variable'),('fixed','Fixed')], 'Cost Type', states={ 'finance_manager':[('readonly', True)]}),
        'activities_line': fields.one2many('tpt.activities.line', 'bom_id', 'Activities', states={'finance_manager':[('readonly', True)]}),
#         'product_cost': fields.function(_norms, store = True, multi='sums', string='Product Cost'),
        'finish_product_cost': fields.function(sum_finish_function, string='Finish Product Cost', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
#         'product_cost': fields.float('Budget Cost'),
        'product_cost': fields.function(_norms, multi='sums', store = True, string='Budget Cost', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'note': fields.text('Notes', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'bom_lines': fields.one2many('mrp.bom', 'bom_id', 'BoM Lines', states={'finance_manager':[('readonly', True)]}),
        'price_unit': fields.float('Unit Price', states={'finance_manager':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('product_manager', 'Production'),('finance_manager', 'Finance')],'Status', readonly=True),
        'location_src_id': fields.many2one('stock.location', 'Production Source Location',
            readonly=True, states={'draft':[('readonly',False)]},
            help="Location where the system will look for components."),
        'location_dest_id': fields.many2one('stock.location', 'Production Destination',
            readonly=True, states={'draft':[('readonly',False)]},
            help="Location where the system will stock the finished products."),
    
    }
    _defaults = {
        'state': 'draft',
                 }
    def location_id_change(self, cr, uid, ids, src, dest, context=None):
        """ Changes destination location if source location is changed.
        @param src: Source location id.
        @param dest: Destination location id.
        @return: Dictionary of values.
        """
        if dest:
            return {}
        if src:
            return {'value': {'location_dest_id': src}}
        return {}
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_norm_id'):
            DATETIME_FORMAT = "%Y-%m-%d"
            now = time.strftime('%Y-%m-%d')
            date_now = datetime.datetime.strptime(now, DATETIME_FORMAT)
            sql = '''
                select id from mrp_bom where '%s' between date_start and date_stop
            '''%(date_now)
            cr.execute(sql)
            mrp_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',mrp_ids)]
        return super(mrp_bom, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def bt_approve_production(self, cr, uid, ids, context=None):
        for bom in self.browse(cr,uid,ids):
            self.write(cr, uid, ids,{'state':'product_manager'})
            activity_obj = self.pool.get('tpt.activities.line')
            sql = '''
                select id from tpt_activities_line where bom_id = %s
            '''%(bom.id)
            cr.execute(sql)
            activity_ids = [r[0] for r in cr.fetchall()]
            activity_obj.write(cr, uid, activity_ids,{'state':'product_manager'})
            sql = '''
                select id from mrp_bom where bom_id = %s
            '''%(bom.id)
            cr.execute(sql)
            bom_one2many_ids = [r[0] for r in cr.fetchall()]
            self.write(cr, uid, bom_one2many_ids,{'state':'product_manager'})
        return True 
    
    def bt_approve_finance(self, cr, uid, ids, context=None):
        for bom in self.browse(cr,uid,ids):
            self.write(cr, uid, ids,{'state':'finance_manager'})
            activity_obj = self.pool.get('tpt.activities.line')
            sql = '''
                select id from tpt_activities_line where bom_id = %s
            '''%(bom.id)
            cr.execute(sql)
            activity_ids = [r[0] for r in cr.fetchall()]
            activity_obj.write(cr, uid, activity_ids,{'state':'finance_manager'})
            sql = '''
                select id from mrp_bom where bom_id = %s
            '''%(bom.id)
            cr.execute(sql)
            bom_one2many_ids = [r[0] for r in cr.fetchall()]
            self.write(cr, uid, bom_one2many_ids,{'state':'finance_manager'})
        return True
    
    def _check_date_id(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if not date.bom_id and date.date_start:
                sql = '''
                    select id from mrp_bom where id != %s and product_id = %s and date_stop > ('%s')
                '''%(date.id,date.product_id.id,date.date_start)
                cr.execute(sql)
                date_ids = [row[0] for row in cr.fetchall()]
                if date_ids:  
                    raise osv.except_osv(_('Warning!'),_('Start Date is not suitable!!!'))
                    return False
        return True
    _constraints = [
        (_check_date_id, 'Identical Data', ['date_stop','product_id']),
    ]
    
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        if 'product_cost' in vals:
            if (vals['product_cost'] < 0):
                raise osv.except_osv(_('Warning!'),_('Product Cost is not negative value'))
        if 'active' in vals and vals['active']:
            product_exist_ids = self.search(cr,uid,[('product_id', '=', vals['product_id']),('active', '=', True),('bom_id','=',False)])
            if product_exist_ids:
                    raise osv.except_osv(_('Warning!'),_('This product was actived'))
        return super(mrp_bom, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(mrp_bom, self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if (line.product_qty < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
            if (line.product_cost < 0):
                raise osv.except_osv(_('Warning!'),_('Product Cost is not allowed as negative values'))
            
            if line.active and not line.bom_id:
                product_exist_ids = self.search(cr,uid,[('product_id', '=', line.product_id.id),('id', '!=', line.id),('active', '=', True),('bom_id','=',False)])
                if product_exist_ids:
                    raise osv.except_osv(_('Warning!'),_('This product was actived'))
        return new_write
            
    def onchange_cost_type(self, cr, uid, ids, product_id=False, cost_type=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            if cost_type == 'fixed':
                vals = {
                        'product_cost': 0.0
                        }
            if cost_type == 'variable':
                sql='''
                    select product_id, sum(product_qty) as product_qty, sum(line_net) as line_net from purchase_order_line where product_id = %s group by product_id
                '''%(product_id)
                cr.execute(sql)
                for status in cr.dictfetchall():
                    vals = {
                            'product_cost': status['line_net']/status['product_qty']
                            }
            
        return {'value': vals}
    
mrp_bom()

class mrp_subproduct(osv.osv):
    _inherit = 'mrp.subproduct'
    _columns={
        'description':fields.text('Description'),
    }

    def create(self, cr, uid, vals, context=None):
        
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        if 'product_qty' in vals:
            if (vals['product_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
        new_id = super(mrp_subproduct, self).create(cr, uid, vals, context)
        return new_id    
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        new_write = super(mrp_subproduct, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if (line.product_qty < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
        return new_write

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        """ Changes UoM if product_id changes.
        @param product_id: Changed product_id
        @return: Dictionary of changed values
        """
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            v = {'product_uom': prod.uom_id.id,'description': prod.name}
            return {'value': v}
        return {}

mrp_subproduct()

class tpt_activities_line(osv.osv):
    _name = 'tpt.activities.line'
    
    def _norms(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for master in self.browse(cr,uid,ids,context=context):
            res[master.id] = {
                    'product_cost': 0.0
                } 
            res[master.id]['product_cost'] = master.product_qty * master.price_unit
            if master.cost_type == 'variable' :
                res[master.id]['product_cost'] = master.product_qty * master.price_unit
#                 sql='''
#                     select product_id, sum(product_qty) as product_qty, sum(line_net) as line_net from purchase_order_line where product_id = %s group by product_id
#                 '''%(master.product_id.id)
#                 cr.execute(sql)
#                 for product in cr.dictfetchall():
#                     res[master.id]['product_cost'] = product['line_net']/product['product_qty']
            if master.cost_type == 'fixed':
                res[master.id]['product_cost'] = master.product_qty * master.price_unit
        return res
    
    _columns = {
        'bom_id': fields.many2one('mrp.bom', 'BoM', ondelete='cascade'),
        'activities_id': fields.many2one('tpt.activities', 'Activities', required=True, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'description':fields.char('Description',size=256, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True, states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'cost_type': fields.selection([('variable','Variable'),('fixed','Fixed')], 'Cost Type', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'product_cost': fields.function(_norms, multi='sums', store = True, string='Budget Cost', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'price_unit': fields.float('Unit Price', states={'finance_manager':[('readonly', True)]}),
        'note': fields.text('Notes', states={'product_manager': [('readonly', True)], 'finance_manager':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('product_manager', 'Production'),('finance_manager', 'Finance')],'Status', readonly=True),
    }
    
    _defaults={
        'state': 'draft',
        'cost_type': 'variable',
        'product_qty': lambda *a: 1.0,
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'product_qty' in vals:
            if (vals['product_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
        new_id = super(tpt_activities_line, self).create(cr, uid, vals, context)
        return new_id    
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(tpt_activities_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if (line.product_qty < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
        return new_write

    def onchange_description(self, cr, uid, ids,activities_id=False,context=None):
        vals = {}
        if activities_id:
            ac = self.pool.get('tpt.activities').browse(cr, uid, activities_id)
            vals = {'description': ac.name,
                    'product_uom': ac.uom_po_id.id }
        return {'value': vals}

tpt_activities_line()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
            
            'move_lines': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Products to Consume',
            domain=[('state','not in', ('done', 'cancel'))], readonly=False, states={'draft':[('readonly',False)]}),
            'move_created_ids': fields.one2many('stock.move', 'production_id', 'Products to Produce',
            domain=[('state','not in', ('done', 'cancel'))], readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
    }
    _defaults={
        'name': '/',
    }
#     def unlink(self, cr, uid, ids, context=None):
#         
#         for production in self.browse(cr, uid, ids, context=context):
#             mrp_production_ids =self.pool.get('mrp.production.product.line').search(cr,uid,[('product_id','=',production.product_id.id)]) 
#             if mrp_production_ids:
#                 self.pool.get('mrp.production.product.line').unlink(cr, uid, mrp_production_ids, context=context)
#         return super(stock_move, self).unlink(cr, uid, ids, context=context)
    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """
        if not bom_id:
            return {'value': {
                'routing_id': False
            }}
        bom_point = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)
        if bom_point.product_id:
            product = self.pool.get('product.product').browse(cr, uid, bom_point.product_id.id, context=context)
            routing_id = bom_point.routing_id.id or False
            product_uom_id = product.uom_id and product.uom_id.id or False
            result = {
                'product_id':bom_point.product_id.id,
                'routing_id': routing_id,
                'product_uom': product_uom_id,
                'location_src_id':bom_point.location_src_id and bom_point.location_src_id.id or False,
                'location_dest_id':bom_point.location_dest_id and bom_point.location_dest_id.id or False,
            }
        return {'value': result}
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        if not product_id:
            return {'value': {
                'product_uom': False,
                'bom_id': False,
                'routing_id': False
            }}
        bom_obj = self.pool.get('mrp.bom')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        bom_id = bom_obj._bom_find(cr, uid, product.id, product.uom_id and product.uom_id.id, [])
        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom_point.routing_id.id or False

        product_uom_id = product.uom_id and product.uom_id.id or False
        result = {
            'product_uom': product_uom_id,
#             'bom_id': bom_id,
            'routing_id': routing_id,
        }
        return {'value': result}

    def create(self, cr, uid, vals, context=None):
        sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        else:
            if vals.get('name','/')=='/':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'production.declaration')
                vals['name'] =  sequence and 'PRD'+'/'+fiscalyear['code']+'/'+sequence or '/'
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        new_id = super(mrp_production, self).create(cr, uid, vals, context=context)   
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        product_line_obj = self.pool.get('mrp.production.product.line')
        for mrp in self.browse(cr,uid,ids):
            if 'move_lines' in vals:
                for line in vals['move_lines']:
                    if line[0]==6:
                        move_ids = line[2]
                        cr.execute('''
                            select move_id from mrp_production_move_ids where production_id = %s and move_id not in %s
                        ''',(mrp.id,tuple(move_ids)),)
                        move_before_ids = [r[0] for r in cr.fetchall()]
                        for move in self.pool.get('stock.move').browse(cr, uid, move_before_ids):
                            product_line_ids = product_line_obj.search(cr, uid, [('product_id','=',move.product_id.id),('product_uom','=',move.product_uom.id)])
                            product_line_obj.unlink(cr, uid, product_line_ids)
        new_write = super(mrp_production, self).write(cr, uid,ids, vals, context)
        return new_write
    
    def _action_compute_lines(self, cr, uid, ids, properties=None, context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """

        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')

        for production in self.browse(cr, uid, ids, context=context):
            #unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.product_lines], context=context)
    
            #unlink workcenter_lines
            workcenter_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.workcenter_lines], context=context)
    
            # search BoM structure and route
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})
    
            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a bill of material for this product."))
    
            # get components and workcenter_lines from BoM structure
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0] # product_lines
            results2 = res[1] # workcenter_lines
    
            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                line['app_qty'] = production.product_qty
                prod_line_obj.create(cr, uid, line)
    
            #reset workcenter_lines in production order
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return results
    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool.get('stock.move')
        source_location_id = production.product_id.property_stock_production.id
        destination_location_id = production.location_dest_id.id
        data = {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production.product_id.id,
            'product_qty': production.product_qty,
            'product_uom': production.product_uom.id,
            'product_uos_qty': production.product_uos and production.product_uos_qty or False,
            'product_uos': production.product_uos and production.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': production.move_prod_id.id,
            'state': 'waiting',
            'company_id': production.company_id.id,
            'app_quantity': production.product_qty,
            'is_tpt_production': True,
        }
        if production.product_id.name in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001') or production.product_id.default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'):
            prodlot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=','temp_tio2')])
            if prodlot_ids:
                data.update({'prodlot_id':prodlot_ids[0]})
        if production.product_id.name in ('TITANIUM DIOXIDE-RUTILE','M0501010008') or production.product_id.default_code in ('TITANIUM DIOXIDE-RUTILE','M0501010008'):
            prodlot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=','temp_tio2_rutile')])
            if prodlot_ids:
                data.update({'prodlot_id':prodlot_ids[0]})
        if production.product_id.name in ('FERROUS SULPHATE','FSH','M0501010002') or production.product_id.default_code in ('FERROUS SULPHATE','FSH','M0501010002'):
            prodlot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=','temp_fsh')])
            if prodlot_ids:
                data.update({'prodlot_id':prodlot_ids[0]})
        move_id = stock_move.create(cr, uid, data, context=context)
        production.write({'move_created_ids': [(6, 0, [move_id])]}, context=context)
        return move_id
    def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        production = production_line.production_id
        # Internal shipment is created for Stockable and Consumer Products
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        destination_location_id = production.product_id.property_stock_production.id
        if not source_location_id:
            source_location_id = production.location_src_id.id
            
        prodlot_ids = []
        if production_line.product_id.default_code in ['FERROUS SULPHATE','FSH','M0501010002'] or production_line.product_id.name in ['FERROUS SULPHATE','FSH','M0501010002']:
            sql = '''
                    select id from stock_production_lot where name='temp_fsh'
                '''
            cr.execute(sql)
            prodlot_ids = cr.fetchone()
            if prodlot_ids and self.pool.get('stock.production.lot').browse(cr, uid, prodlot_ids[0]).stock_available<production_line.product_qty:
                raise osv.except_osv(_('Warning!'),'Available stock is not enough for the selected raw material!')
            
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production_line.product_id.id,
            'product_qty': production_line.product_qty,
            'product_uom': production_line.product_uom.id,
            'product_uos_qty': production_line.product_uos and production_line.product_uos_qty or False,
            'product_uos': production_line.product_uos and production_line.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': parent_move_id,
            'state': 'waiting',
            'company_id': production.company_id.id,
            'prodlot_id': prodlot_ids and prodlot_ids[0] or False,
            'app_quantity': production_line.product_qty,
            'is_tpt_production': True,
        })
        production.write({'move_lines': [(4, move_id)]}, context=context)
        return move_id
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_mrp_tio2_batch', False) and context.get('product_id', False):
            sql = '''
                select id from mrp_production where product_id=%s and id not in (select mrp_id from tpt_tio2_batch_split)
            '''%(context.get('product_id'))
            cr.execute(sql)
            mrp_ids = [row[0] for row in cr.fetchall()]
            if context.get('mrp_id', False):
                mrp_ids.append(context.get('mrp_id'))
            args += [('id','in',mrp_ids)]
        if context.get('search_mrp_fsh_batch', False) and context.get('product_id', False):
            sql = '''
                select id from mrp_production where product_id=%s and id not in (select mrp_id from tpt_fsh_batch_split)
            '''%(context.get('product_id'))
            cr.execute(sql)
            mrp_ids = [row[0] for row in cr.fetchall()]
            if context.get('mrp_id', False):
                mrp_ids.append(context.get('mrp_id'))
            args += [('id','in',mrp_ids)]
        return super(mrp_production, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms production order and calculates quantity based on subproduct_type.
        @return: Newly generated picking Id.
        """
        shipment_id = False
        wf_service = netsvc.LocalService("workflow")
        uncompute_ids = filter(lambda x:x, [not x.product_lines and x.id or False for x in self.browse(cr, uid, ids, context=context)])
        self.action_compute(cr, uid, uncompute_ids, context=context)
        for production in self.browse(cr, uid, ids, context=context):
            shipment_id = self._make_production_internal_shipment(cr, uid, production, context=context)
            produce_move_id = self._make_production_produce_line(cr, uid, production, context=context)

            # Take routing location as a Source Location.
            source_location_id = production.location_src_id.id
            if production.routing_id and production.routing_id.location_id:
                source_location_id = production.routing_id.location_id.id

            for line in production.product_lines:
                consume_move_id = self._make_production_consume_line(cr, uid, line, produce_move_id, source_location_id=source_location_id, context=context)
                if shipment_id:
                    shipment_move_id = self._make_production_internal_shipment_line(cr, uid, line, shipment_id, consume_move_id,\
                                 destination_location_id=source_location_id, context=context)
                    self._make_production_line_procurement(cr, uid, line, shipment_move_id, context=context)

            if shipment_id:
                wf_service.trg_validate(uid, 'stock.picking', shipment_id, 'button_confirm', cr)
            production.write({'state':'confirmed'}, context=context)
            
        picking_id = shipment_id
        product_uom_obj = self.pool.get('product.uom')
        for production in self.browse(cr, uid, ids):
            source = production.product_id.property_stock_production.id
            if not production.bom_id:
                continue
            for sub_product in production.bom_id.sub_products:
                product_uom_factor = product_uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.bom_id.product_uom.id)
                qty1 = sub_product.product_qty
                qty2 = production.product_uos and production.product_uos_qty or False
                product_uos_factor = 0.0
                if qty2 and production.bom_id.product_uos.id:
                    product_uos_factor = product_uom_obj._compute_qty(cr, uid, production.product_uos.id, production.product_uos_qty, production.bom_id.product_uos.id)
                if sub_product.subproduct_type == 'variable':
                    if production.product_qty:
                        qty1 *= product_uom_factor / (production.bom_id.product_qty or 1.0)
                    if production.product_uos_qty:
                        qty2 *= product_uos_factor / (production.bom_id.product_uos_qty or 1.0)
                data = {
                    'name': 'PROD:'+production.name,
                    'date': production.date_planned,
                    'product_id': sub_product.product_id.id,
                    'product_qty': qty1,
                    'product_uom': sub_product.product_uom.id,
                    'product_uos_qty': qty2,
                    'product_uos': production.product_uos and production.product_uos.id or False,
                    'location_id': source,
                    'location_dest_id': production.location_dest_id.id,
                    'move_dest_id': production.move_prod_id.id,
                    'state': 'waiting',
                    'production_id': production.id,
                    'app_quantity': qty1,
                    'is_tpt_production': True,
                }
                self.pool.get('stock.move').create(cr, uid, data)
        return picking_id
    
    def force_production(self, cr, uid, ids, *args):
        """ Assigns products.
        @param *args: Arguments
        @return: True
        """
        ### Kiem tra so luong nguyen lieu trong kho Raw Materials Location
        for production in self.browse(cr, uid, ids, context = None):
            for line in production.move_lines:
                sql = '''
                                select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_dest_id = %s
                                    union all
                                    select st.product_qty*-1
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_id = %s
                                    )foo
                '''%(line.product_id.id,production.location_src_id.id,line.product_id.id,production.location_src_id.id)
                cr.execute(sql)
                ton_sl = cr.dictfetchone()['ton_sl']
                if line.product_qty > ton_sl:
                    raise osv.except_osv(_('Warning!'),_('Do not have enough quantity for raw material %s in stock %s!' %(line.product_id.default_code, production.location_src_id.name)))
                
        ###
        pick_obj = self.pool.get('stock.picking')
        pick_obj.force_assign(cr, uid, [prod.picking_id.id for prod in self.browse(cr, uid, ids)])
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the production order and related stock moves.
        @return: True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        for production in self.browse(cr, uid, ids, context=context):
            if production.state == 'confirmed' and production.picking_id.state=='done':
                raise osv.except_osv(
                    _('Cannot cancel manufacturing order!'),
                    _('You must first cancel related internal picking attached to this manufacturing order.'))
            if production.move_created_ids:
                move_obj.action_cancel(cr, uid, [x.id for x in production.move_created_ids])
            move_obj.action_cancel(cr, uid, [x.id for x in production.move_lines])
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

mrp_production()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    _columns = {
        'location_id':fields.many2one('stock.location','Location'),
        'application_id':fields.many2one('crm.application','Application')
    }
    
    def init(self, cr):
        product_ids = self.pool.get('product.product').search(cr, 1, ['|',('name','in',['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']),('default_code','in',['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'])])
        if product_ids:
            sql = '''
                select id from stock_production_lot where product_id = %s and name='temp_tio2'
            '''%(product_ids[0])
            cr.execute(sql)
            prodlot_ids = [r[0] for r in cr.fetchall()]
            if not prodlot_ids:
                self.create(cr, 1, {'name': 'temp_tio2', 'phy_batch_no': 'temp_tio2', 'product_id': product_ids[0]})
        
        product_ids = self.pool.get('product.product').search(cr, 1, ['|',('name','in',['TITANIUM DIOXIDE-RUTILE','M0501010008']),('default_code','in',['TITANIUM DIOXIDE-RUTILE','M0501010008'])])
        if product_ids:
            sql = '''
                select id from stock_production_lot where product_id = %s and name='temp_tio2_rutile'
            '''%(product_ids[0])
            cr.execute(sql)
            prodlot_ids = [r[0] for r in cr.fetchall()]
            if not prodlot_ids:
                self.create(cr, 1, {'name': 'temp_tio2_rutile', 'phy_batch_no': 'temp_tio2_rutile', 'product_id': product_ids[0]})
                
        product_ids = self.pool.get('product.product').search(cr, 1, ['|',('name','in',['FERROUS SULPHATE','FSH','M0501010002']),('default_code','in',['FERROUS SULPHATE','FSH','M0501010002'])])
        if product_ids:
            for lot_name in ['AGRI','WET','DRIER','temp_fsh']:
                sql = '''
                    select id from stock_production_lot where product_id = %s and name = '%s'
                '''%(product_ids[0],lot_name)
                cr.execute(sql)
                prodlot_ids = [r[0] for r in cr.fetchall()]
                if not prodlot_ids:
                    self.create(cr, 1, {'name': lot_name, 'phy_batch_no': lot_name, 'product_id': product_ids[0]})

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_batch_no_tio2'):
            sql = '''
                select id from stock_production_lot where product_id in (select id from product_product where name_template in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001') or default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'))
            '''
            cr.execute(sql)
            mrp_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',mrp_ids)]
        if context.get('search_prodlot_id',False) and context.get('location_id',False):
            sql = '''
                select id from stock_production_lot where location_id = %s
            '''%(context.get('location_id'))
            cr.execute(sql)
            prodlot_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',prodlot_ids)]
        return super(stock_production_lot, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def unlink(self, cr, uid, ids, context=None):
        lot_name = self.read(cr, uid, ids, ['name'], context=context)
        unlink_ids = []
        for lot in lot_name:
            if lot['name'] in ('temp_tio2','Argi','Wet','Drier','temp_fsh'):
                raise osv.except_osv(_('Warning!'), _('This Batch Number can not be deleted. It is default Batch Number!'))
            else:
                unlink_ids.append(lot['id'])
        return super(stock_production_lot, self).unlink(cr, uid, ids, context=context)
   
stock_production_lot()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'app_quantity': fields.float('Required Quantity'),
        'is_tpt_production': fields.boolean('Is tpt production'),
    }

    


        
    def onchange_app_qty_id(self, cr, uid, ids,app_quantity, product_qty,context=None):
        vals = {}
#         if app_quantity > product_qty:
#             if app_quantity > product_qty:
#                 warning = {  
#                           'title': _('Warning!'),  
#                           'message': _('Applied Quantity is not greater than Product Quantity!'),  
#                           }  
#                 vals['app_quantity']=product_qty
#                 return {'value': vals,'warning':warning}
#         if app_quantity < 0 :
#             warning = {  
#                           'title': _('Warning!'),  
#                           'message': _('Applied Quantity is not allowed as negative values !'),  
#                           }  
#             vals['app_quantity']=product_qty
#             return {'value': vals,'warning':warning}
        return {'value': vals}
    
    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos,is_tpt_production=False,app_quantity=False):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        #TPT COMMENTED BY BalamuruganPurushothaman - 29/03/2015 - TO AVOID THROW THIS ERROR IN PRODUCTION DECLARATION SCREEN
        #=======================================================================
#         if app_quantity and product_qty > app_quantity:
#             vals = {}
#             warning = {  
#                           'title': _('Warning!'),  
#                           'message': _('Applied Quantity is not greater than Product Quantity!'),  
#                           }  
#             vals['product_qty']=app_quantity
#             return {'value': vals,'warning':warning}
        #=======================================================================
        result = {
                  'product_uos_qty': 0.00
          }
        warning = {}
        if ids and is_tpt_production:
            mrp_product_line_obj = self.pool.get('mrp.production.product.line')
            cr.execute('select production_id from mrp_production_move_ids where move_id in %s group by production_id',(tuple(ids),))
            production_ids = [row[0] for row in cr.fetchall()]
            for move_line in self.browse(cr, uid, ids):
                mrp_product_line_ids = mrp_product_line_obj.search(cr, uid, [('production_id','in',production_ids),('product_id','=',move_line.product_id.id),('product_uom','=',move_line.product_uom.id)])
                mrp_product_line_obj.write(cr, uid, mrp_product_line_ids,{'product_qty':product_qty})
        if (not product_id) or (product_qty <=0.0):
            result['product_qty'] = 0.0
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        
        # Warn if the quantity was decreased 
        if ids:
            for move in self.read(cr, uid, ids, ['product_qty']):
                if product_qty < move['product_qty'] and not is_tpt_production:
                    warning.update({
                       'title': _('Information'),
                       'message': _("By changing this quantity here, you accept the "
                                "new quantity as complete: OpenERP will not "
                                "automatically generate a back order.") })
                break

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty

        return {'value': result, 'warning': warning}
stock_move()
# class tpt_quality_verification(osv.osv):
#     _name = 'tpt.quality.verification'
#     _columns = {
#         'product_id': fields.many2one('product.product', 'Product', required=True),
#         'name': fields.date('Created Date'),
#         'mrp_id': fields.many2one('mrp.production', 'Production Decl. No', required=True),
#         'location_id': fields.many2one('stock.location', 'Warehouse Location', required=True),
#         'available': fields.related('mrp_id', 'product_qty',string='Available Stock',store=True,readonly=True),
#         'stating_batch_no': fields.char('Stating Batch No', size=100),
#         'batch_split_line': fields.one2many('tpt.batch.split.line', 'tio2_id', 'Batch Split Line'),
#         'state':fields.selection([('draft', 'Draft'),('generate', 'Generated'),('confirm', 'Confirm')],'Status', readonly=True),
#     }
#     
# tpt_quality_verification()
class tpt_quality_verification(osv.osv):
    _name = 'tpt.quality.verification'
    _columns = {
        'prod_batch_id': fields.many2one('stock.production.lot','Production Batch No',required=True, states={ 'done':[('readonly', True)]}),
        'product_id':fields.many2one('product.product','Product', states={ 'done':[('readonly', True)]}),
        'product_type': fields.selection([('rutile', 'Rutile'),('anatase', 'Anatase')],'Product Type', states={ 'done':[('readonly', True)]}),
        'warehouse_id':fields.many2one('stock.location','Warehouse location', states={ 'done':[('readonly', True)]}),
        'phy_batch_no': fields.char('Physical Batch No', size=100, states={ 'done':[('readonly', True)]}),
        'name':fields.datetime('Created Date',readonly=True),
        'batch_quality_line':fields.one2many('crm.application.line', 'batch_verifi_id','Batch Quality', states={ 'done':[('readonly', True)]}),
        'applicable_id':fields.many2one('crm.application','Applicable for', states={ 'done':[('readonly', True)]}),
        'phy_batch_no': fields.char('Physical Batch No', size=100, states={ 'done':[('readonly', True)]}),
        'location': fields.char('Location', size=100, states={ 'done':[('readonly', True)]}),
        'weight': fields.char('Weight', size=100, states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Updated')],'Status', readonly=True),
    }
    _defaults={
        'name':time.strftime('%Y-%m-%d %H:%M:%S'),
        'state':'draft',
    }
    def bt_update(self, cr, uid, ids, context=None):
        for quality in self.browse(cr,uid,ids):
            sql='''
                update stock_production_lot set phy_batch_no='%s',application_id=%s where id =%s
            '''%(quality.phy_batch_no,quality.applicable_id.id,quality.prod_batch_id.id)
            cr.execute(sql)
        
        return self.write(cr, uid, ids,{'state':'done'})
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def onchange_prod_batch_id(self, cr, uid, ids,prod_batch_id=False,context=None):
        vals = {}
        if prod_batch_id:
            prod_batch = self.pool.get('stock.production.lot').browse(cr, uid, prod_batch_id)
            vals = {'warehouse_id': prod_batch.location_id and prod_batch.location_id.id or False,
                    'product_id': prod_batch.product_id and prod_batch.product_id.id or False}
        return {'value': vals}
    
    def onchange_applicable_id(self, cr, uid, ids,applicable_id=False,context=None):
        vals = {}
        if applicable_id :
            details = []
            appli = self.pool.get('crm.application').browse(cr, uid, applicable_id)
            for para in appli.application_line:
                rs = {
                      'parameters_id':para.parameters_id and para.parameters_id.id or False,
                      'standard_value': para.standard_value or False,
                      }
                details.append((0,0,rs))
                     
        return {'value': {'batch_quality_line': details}}

tpt_quality_verification()

# class tpt_batch_quality_verification_line(osv.osv):
#     _name = 'tpt.batch.quality.verification.line'
#     _columns = {
#         'batch_verifi_id': fields.many2one('quality.verification','Batch Quality',ondelete='cascade'),
#         'stand_value':fields.float('Standard Value'),
#         'exp_value':fields.float('Experiment Value'),
#         'parameter_id':fields.many2one('tpt.quality.parameters','Parameters',required=True),
#     }
# tpt_batch_quality_verification_line()

class mrp_production_product_line(osv.osv):
    _inherit = 'mrp.production.product.line'
    _columns = {
            'app_qty':fields.float('Required Quantity')
            
    }

    _defaults={
               'app_qty':0.0,
    }   
    
    
mrp_production_product_line()    
