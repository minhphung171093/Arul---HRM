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
            for num in range(0,int(line.available)):
                prodlot_name = self.pool.get('ir.sequence').get(cr, uid, 'batching.tio2')
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
    
                cr.execute("SELECT setval('ir_sequence_%03d',nextval('ir_sequence_%03d')-1)+1" % (seq['id'],seq['id']))
                seq['number_next'] = cr.fetchone()
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
            
            vals['stating_batch_no'] = sequence or '/'
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
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'name': fields.date('Created Date'),
        'mrp_id': fields.many2one('mrp.production', 'Production Decl. No', required=True),
        'location_id': fields.many2one('stock.location', 'Warehouse Location', required=True),
        'available': fields.related('mrp_id', 'product_qty',string='Available Stock',store=True,readonly=True),
        'batch_split_line': fields.one2many('tpt.fsh.batch.split.line', 'fsh_id', 'Batch Split Line'),
        'state':fields.selection([('draft', 'Draft'),('confirm', 'Confirm')],'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'name': time.strftime('%Y-%m-%d'),
    }
    
    def bt_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_split_obj = self.pool.get('stock.move.split')
        move_obj = self.pool.get('stock.move')
        for line in self.browse(cr, uid, ids):
            move_ids = move_obj.search(cr, uid, [('scrapped','=',False),('production_id','=',line.mrp_id.id),('product_id','=',line.product_id.id)])
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
            v = {'available': mrp.product_qty,'location_id': mrp.location_dest_id.id}
            return {'value': v}
        return {}
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(tpt_fsh_batch_split, self).create(cr, uid, vals, context=context)
        new = self.browse(cr, uid, new_id)
        sum = 0
        for line in new.batch_split_line:
            sum+=line.qty
        if sum!=new.available:
            raise osv.except_osv(_('Warning!'),_('The sum of Qtys entered in the Batch split should match with the available stock quantity entered at the header'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(tpt_fsh_batch_split, self).write(cr, uid,ids, vals, context)
        for new in self.browse(cr, uid, ids):
            sum = 0
            for line in new.batch_split_line:
                sum+=line.qty
            if sum!=new.available:
                raise osv.except_osv(_('Warning!'),_('The sum of Qtys entered in the Batch split should match with the available stock quantity entered at the header'))
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
        'product_id': fields.many2one('product.product', 'Product', required = True),
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
        (_check_product_id, 'Identical Data', ['product_id']),
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
     
     
    def create(self, cr, uid, vals, context=None):
        
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        new_id = super(mrp_bom, self).create(cr, uid, vals, context)
        return new_id    
     
    def _norms(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for master in self.browse(cr,uid,ids,context=context):
            res[master.id] = {
                    'product_cost': 0.0,
                } 
            if master.cost_type == 'variable' :
                sql='''
                    select product_id, sum(product_qty) as product_qty, sum(line_net) as line_net from purchase_order_line where product_id = %s group by product_id
                '''%(master.product_id.id)
                cr.execute(sql)
                for product in cr.dictfetchall():
                    res[master.id]['product_cost'] = product['line_net']/product['product_qty']
            if master.cost_type == 'fixed':
                res[master.id]['product_cost'] = master.product_id.standard_price
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
        'cost_type': fields.selection([('variable','Variable'),('fixed','Fixed')], 'Cost Type'),
        'activities_line': fields.one2many('tpt.activities.line', 'bom_id', 'Activities'),
#         'product_cost': fields.function(_norms, store = True, multi='sums', string='Product Cost'),
        'finish_product_cost': fields.function(sum_finish_function, string='Finish Product Cost'),
        'product_cost': fields.float('Product Cost'),
    }
    
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
        new_id = super(mrp_subproduct, self).create(cr, uid, vals, context)
        return new_id    

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
    _columns = {
        'bom_id': fields.many2one('mrp.bom', 'BoM', ondelete='cascade'),
        'activities_id': fields.many2one('tpt.activities', 'Activities', required=True),
        'description':fields.char('Description',size=256),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'cost_type': fields.selection([('variable','Variable'),('fixed','Fixed')], 'Cost Type'),
        'product_cost': fields.float('Cost'),
    }
    
    _defaults={
        'cost_type': 'variable',
        'product_qty': lambda *a: 1.0,
    }

    def onchange_description(self, cr, uid, ids,activities_id=False,context=None):
        vals = {}
        if activities_id:
            ac = self.pool.get('tpt.activities').browse(cr, uid, activities_id)
            vals = {'description': ac.name }
        return {'value': vals}

tpt_activities_line()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
            'move_lines': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Products to Consume',
            domain=[('state','not in', ('done', 'cancel'))], readonly=False, states={'draft':[('readonly',False)]}),
    }
    _defaults={
        'name': '/',
    }

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
        }
        if production.product_id.name in ('TITANIUM DIOXIDE-ANATASE','TiO2') or production.product_id.default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2'):
            prodlot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=','temp_tio2')])
            if prodlot_ids:
                data.update({'prodlot_id':prodlot_ids[0]})
        if production.product_id.name in ('FERROUS SULPHATE','FSH') or production.product_id.default_code in ('FERROUS SULPHATE','FSH'):
            prodlot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=','temp_fsh')])
            if prodlot_ids:
                data.update({'prodlot_id':prodlot_ids[0]})
        move_id = stock_move.create(cr, uid, data, context=context)
        production.write({'move_created_ids': [(6, 0, [move_id])]}, context=context)
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
    
mrp_production()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    _columns = {
        'location_id':fields.many2one('stock.location','Location'),
    }
    
    def init(self, cr):
        product_ids = self.pool.get('product.product').search(cr, 1, ['|',('name','in',['TITANIUM DIOXIDE-ANATASE','TiO2']),('default_code','in',['TITANIUM DIOXIDE-ANATASE','TiO2'])])
        if product_ids:
            sql = '''
                select id from stock_production_lot where product_id = %s and name='temp_tio2'
            '''%(product_ids[0])
            cr.execute(sql)
            prodlot_ids = [r[0] for r in cr.fetchall()]
            if not prodlot_ids:
                self.create(cr, 1, {'name': 'temp_tio2', 'phy_batch_no': 'temp_tio2', 'product_id': product_ids[0]})
        
        product_ids = self.pool.get('product.product').search(cr, 1, ['|',('name','in',['FERROUS SULPHATE','FSH']),('default_code','in',['FERROUS SULPHATE','FSH'])])
        if product_ids:
            for lot_name in ['Argi','Wet','Drier','temp_fsh']:
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
                select id from stock_production_lot where product_id in (select id from product_product where name_template in ('TITANIUM DIOXIDE-ANATASE','TiO2') or default_code in ('TITANIUM DIOXIDE-ANATASE','TiO2'))
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
   
stock_production_lot()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'app_quantity': fields.float('Appllied Quantity'),
    }
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(stock_move, self).create(cr, uid, vals, context)
        if 'app_quantity' in vals:
            if (vals['app_quantity'] < 0):
                raise osv.except_osv(_('Warning!'),_('Appllied Quantity is not allowed as negative values'))
        return new_id  
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_move, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.app_quantity < 0:
                raise osv.except_osv(_('Warning!'),_('Appllied Quantity is not allowed as negative values'))
        return new_write  
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
        'phy_batch_no': fields.char('Physical Batch No', size=100,required=True, states={ 'done':[('readonly', True)]}),
        'name':fields.datetime('Created Date',readonly=True),
        'batch_quality_line':fields.one2many('crm.application.line', 'batch_verifi_id','Batch Quality', states={ 'done':[('readonly', True)]}),
        'applicable_id':fields.many2one('crm.application','Applicable for', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Updated')],'Status', readonly=True),
    }
    _defaults={
        'name':time.strftime('%Y-%m-%d %H:%M:%S'),
        'state':'draft',
    }
    def bt_update(self, cr, uid, ids, context=None):
        for quality in self.browse(cr,uid,ids):
            sql='''
                update stock_production_lot set phy_batch_no='%s' where id =%s
            '''%(quality.phy_batch_no,quality.prod_batch_id.id)
            cr.execute(sql)
        
        return self.write(cr, uid, ids,{'state':'done'})
    
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
