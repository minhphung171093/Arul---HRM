# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    _order = "create_date desc"
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        vals['lead_code']= self.pool.get('ir.sequence').get(cr, user, 'lead.code')
        if vals.get('partner_id') and vals['partner_id']:
            partner = self.pool.get('res.partner').browse(cr, user, vals['partner_id'], context=context)
            vals['customer_code'] = partner.customer_code
        new_id = super(crm_lead, self).create(cr, user, vals, context)
        return new_id
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('partner_id') and vals['partner_id']:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
            vals['customer_code'] = partner.customer_code
        res = super(crm_lead, self).write(cr, uid, ids, vals, context=context)
        return res
    
    
    def onchange_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'user_id':emp.user_id.id}
        return {'value': vals}
    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_name' : partner.name,
                'street' : partner.street,
                'street2' : partner.street2,
                'city' : partner.city,
                'state_id' : partner.state_id and partner.state_id.id or False,
                'country_id' : partner.country_id and partner.country_id.id or False,
                'email_from' : partner.email,
                'phone' : partner.phone,
                'mobile' : partner.mobile,
                'fax' : partner.fax,
                'customer_code' : partner.customer_code,
            }
        return {'value' : values}
    
    def get_product(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for lead in self.browse(cursor, user, ids, context=context):
            if lead.lead_line:
                res[lead.id] = lead.lead_line[0].product_id.id
        return res
    
    def get_quotation_status(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        team = False
        for lead in self.browse(cursor, user, ids, context=context):
            if lead.history_ids:
                for line in lead.history_ids:
                    if line.status == 'quotation':
                        team = True
            res[lead.id] = team
        return res
    
    _columns = {
        'name': fields.char('Subject', size=64, select=1),
        'lead_line': fields.one2many('crm.lead.line','lead_id','Lead Line'),
        'lead_type': fields.selection([ ('manufacturer','Manufacturer'), ('trader','Trader'), ],'Lead Type'),
        'lead_zone': fields.selection([('north','North'),('east','East'),('west','West'),('south','South')],'Zone'),
        'competitor_name': fields.char('Competitor Name',size=128),
        'lead_source_id': fields.many2one('crm.leadsource','Lead Source'),
        'probability': fields.float('Probability',degits=(16,2)),
        'customer_expected_price': fields.float('Competitive/Expected Price',degits=(16,2)),
        'expected_revenue': fields.float('Expected Revenue',degits=(16,2)),
        'rating': fields.selection([('01','01'),('02','02'),('03','03'),('04','04'),('05','05'),('06','06'),('07','07'),('08','08'),('09','09'),('10','10')],'Rating'),
        'contact_line': fields.one2many('res.partner', 'crm_lead_id', 'Contacts'),
        'customer_address_line': fields.one2many('customer.address', 'crm_lead_id', 'Customer Locations'),
        'lead_code': fields.char('Lead Code',size=128,readonly=True),
        'customer_code': fields.char('Customer Code',size=128,readonly=True),
        'basic_price': fields.float('Basic Price of Competitor',degits=(16,2)),
        'landed_price': fields.float('Landed Price of Competitor',degits=(16,2)),
        'employee_id': fields.many2one('hr.employee', 'Salesperson', select=True, track_visibility='onchange'),
        'lead_group': fields.selection([ ('domestic','Domestic'), ('export','Export'), ],'Lead Group'),
        'currency_id': fields.many2one('res.currency','Currency',required=True),
        'constitution': fields.selection([ ('company','Company'), ('individual','Individual'),('partnership_firm','Partnership Firm'), ('private_ltd','Private Ltd') ],'Constitution'),
        'contact_last_name': fields.char('Last Name', size=64),
        'status': fields.selection([('new','New'),('opportunity', 'Opportunity'),('quotation', 'Quotation'),
                                    ('awaiting_qc_results','Awaiting QC Results'),('qc_test_completed', 'QC Test Completed'),('sample_received', 'Sample Received'),
                                    ('sample_request','Sample Request'),('awaiting_for_sample_acceptance', 'Awaiting for Sample Acceptance'),('sample_matched', 'Sample Matched'),
                                    ('sample_mismatched','Sample Mismatched'),('cancelled', 'Cancelled'),('won', 'Won'),('closed', 'Closed')],string='Lead Status', size=128,readonly=True),
        'history_ids': fields.one2many('crm.lead.history','lead_id','History',readonly=True),
        'from_existing_customer' : fields.boolean('From Existing Customer'),
        'product_id':fields.function(get_product, string='product', type='many2one', relation='product.product', ondelete="cascade"),
        'quotation_status':fields.function(get_quotation_status, string='Quotation Status', type='boolean',ondelete="cascade"),
    }
    
    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        partner = self.pool.get('res.partner')
        vals = {'name': name,
                'last_name':lead.contact_last_name or False,
                'user_id': lead.user_id.id,
                'comment': lead.description,
                'section_id': lead.section_id.id or False,
                'parent_id': parent_id,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': lead.email_from or False,
                'fax': lead.fax,
                'title': lead.title and lead.title.id or False,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id and lead.country_id.id or False,
                'state_id': lead.state_id and lead.state_id.id or False,
                'is_company': False,
                'type': 'contact',
                'zone_id': lead.lead_zone,
                'customer_code':lead.customer_code
        }
        partner = partner.create(cr, uid, vals, context=context)
        return partner
    
    def _convert_opportunity_data(self, cr, uid, lead, customer, section_id=False, context=None):
        crm_stage = self.pool.get('crm.case.stage')
        contact_id = False
        if customer:
            contact_id = self.pool.get('res.partner').address_get(cr, uid, [customer.id])['default']
        if not section_id:
            section_id = lead.section_id and lead.section_id.id or False
        val = {
            'planned_revenue': lead.planned_revenue,
            'probability': lead.probability,
            'name': lead.name,
            'partner_id': customer and customer.id or False,
            'user_id': (lead.user_id and lead.user_id.id),
            'type': 'opportunity',
            'date_action': fields.datetime.now(),
            'date_open': fields.datetime.now(),
            'email_from': customer and customer.email or lead.email_from,
            'phone': customer and customer.phone or lead.phone,
            'status': 'opportunity',
        }
        if not lead.stage_id or lead.stage_id.type=='lead':
            val['stage_id'] = self.stage_find(cr, uid, [lead], section_id, [('state', '=', 'draft'),('type', 'in', ('opportunity','both'))], context=context)
        return val
    
    def convert_opportunity(self, cr, uid, ids, partner_id, user_ids=False, section_id=False, context=None):
        customer = False
        if partner_id:
            partner = self.pool.get('res.partner')
            customer = partner.browse(cr, uid, partner_id, context=context)
        for lead in self.browse(cr, uid, ids, context=context):
            if lead.state in ('done', 'cancel'):
                continue
            vals = self._convert_opportunity_data(cr, uid, lead, customer, section_id, context=context)
            self.write(cr, uid, [lead.id], vals, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':lead.id,'status':'opportunity'}, context=context)
        self.message_post(cr, uid, ids, body=_("Lead <b>converted into an Opportunity</b>"), subtype="crm.mt_lead_convert_to_opportunity", context=context)

        if user_ids or section_id:
            self.allocate_salesman(cr, uid, ids, user_ids, section_id, context=context)

        return True
    
    def _create_partner(self, cr, uid, ids, context=None):
        """
        Create partner based on action.
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by crm_lead2opportunity_partner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        for data in self.browse(cr, uid, ids, context=context):
            partner_id = data.partner_id and data.partner_id.id or False
            return lead.handle_partner_assignation(cr, uid, ids, 'create', partner_id, context=context)
    
    def _convert_opportunity(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        res = False
        partner_ids_map = self._create_partner(cr, uid, ids, context=context)
        partner_id = partner_ids_map.get(ids[0], False)
        # FIXME: cannot pass user_ids as the salesman allocation only works in batch
        res = lead.convert_opportunity(cr, uid, ids, partner_id, [], False, context=context)
        # FIXME: must perform salesman allocation in batch separately here
        user_ids = vals.get('user_ids', False)
        if user_ids:
            lead.allocate_salesman(cr, uid, ids, user_ids, team_id=False, context=context)
        return res
    
    def apply_convert_to_oppotunities(self, cr, uid, ids, context=None):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        if context is None:
            context = {}
        self._convert_opportunity(cr, uid, ids, {'lead_ids': ids}, context=context)

        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, ids[0], context=context)
    
    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100 """
        for lead in self.browse(cr, uid, ids):
            self.pool.get('crm.lead').write(cr, uid, [lead.id], {'status':'won'}, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':lead.id,'status':'won'}, context=context)
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0),('on_change','=',True)], context=context)
            if stage_id:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 100.0}, new_stage_id=stage_id, context=context)
        return True
    def case_mark_lost(self, cr, uid, ids, context=None):
        """ Mark the case as lost: state=cancel and probability=0 """
        for lead in self.browse(cr, uid, ids):
            self.pool.get('crm.lead').write(cr, uid, [lead.id], {'status':'closed'}, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':lead.id,'status':'closed'}, context=context)
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0),('on_change','=',True)], context=context)
            if stage_id:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 0.0}, new_stage_id=stage_id, context=context)
        return True

    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name','lead_code'], context)
 
        for record in reads:
            name = record['name']
            if record['lead_code']:
                name += ' - '+ record['lead_code']
            res.append((record['id'], name))
        return res
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('specification_lead'):
            sql = '''
                select lead_id from crm_specification where lead_id is not null
            '''
            cr.execute(sql)
            specification_lead_ids = [row[0] for row in cr.fetchall()]
            lead_ids = self.search(cr, uid, [('id','not in',specification_lead_ids),('type','=','opportunity')])
            if context.get('lead_id'):
                lead_ids.append(context.get('lead_id'))
            args += [('id','in',lead_ids)]
        elif context.get('sample_request_lead'):
            sql = '''
                select lead_id from crm_sample_request where lead_id is not null
            '''
            cr.execute(sql)
            sample_request_lead_ids = [row[0] for row in cr.fetchall()]
            lead_ids = self.search(cr, uid, [('id','not in',sample_request_lead_ids),('type','=','opportunity')])
            if context.get('lead_id'):
                lead_ids.append(context.get('lead_id'))
            args += [('id','in',lead_ids)]
        return super(crm_lead, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def create_quotation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.pop('default_state', False)        
        case_obj = self.pool.get('crm.lead')
        crm_sale_obj = self.pool.get('crm.sale.order')
        crm_sale_line_obj = self.pool.get('crm.sale.order.line')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for case in self.browse(cr, uid, ids, context=context):
            new_ids = []
            if case.partner_id:
                partner = case.partner_id
                fpos = partner.property_account_position and partner.property_account_position.id or False
                payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                        ['default', 'invoice', 'delivery', 'contact'])
                pricelist = partner.property_product_pricelist.id
            else:
                raise osv.except_osv(_('Warning!'), _('Customer does not exist'))
#             if False in partner_addr.values():
#                 raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))
            cmpny_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
            shop = self.pool.get('sale.shop').search(cr, uid, [('company_id', '=', cmpny_id)])
            description = ''
            if case.lead_group and case.lead_group == 'domestic':
                description = '*The above price is on ex-works basis. Freight charges will be to your account. (Transporter to be nominated by yourselves) \n*Insurance and statuary levies should be arranged at your end.'
            elif case.lead_group and case.lead_group == 'export':
                description = '*Freight charges will be to your account. (Liner to be nominated by yourselves). \n*Insurance and statuary levies should be arranged at your end.'
            else:
                description =''
            vals = {
                'origin': _('Opportunity: %s') % str(case.id),
                'section_id': case.section_id and case.section_id.id or False,
#                 'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                'shop_id': shop[0],
                'partner_id': partner.id,
                'pricelist_id': pricelist,
#                 'partner_invoice_id': partner_addr['invoice'],
#                 'partner_shipping_id': partner_addr['delivery'],
#                 'partner_invoice_id': partner.id,
#                 'partner_shipping_id': partner.id,
                'date_order': fields.date.context_today(self,cr,uid,context=context),
                'fiscal_position': fpos,
                'payment_term':payment_term,
                'lead_id':case.id,
                'currency_id':case.currency_id.id or False,
                'quotation_type':case.lead_group or False,
                'description':description
                
            }
            if partner.id:
                vals['user_id'] = partner.user_id and partner.user_id.id or uid
            new_id = crm_sale_obj.create(cr, uid, vals, context=context)
            self.pool.get('crm.lead').write(cr, uid, [case.id], {'status':'quotation'}, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':case.id,'status':'quotation'}, context=context)
            #Hung them order line
            for line in case.lead_line:
                vals_line = {
                    'order_id': new_id,
                    'name': line.product_id.name_template or '/',
                    'product_id':line.product_id.id,
                    'application_id':line.application_id.id,
                    'price_unit':0.0,
                    'type':'make_to_stock',
                    'product_uom_qty': 0.0,
                    'product_uom':line.uom_id.id,
                    'product_uos_qty':0.0,
                    'delay':7.0,
                    'state':"draft",                        
                    }
                crm_sale_line_obj.create(cr, uid, vals_line, context=context)
            crm_sale_order = crm_sale_obj.browse(cr, uid, new_id, context=context)
#             case_obj.write(cr, uid, [case.id], {'ref': 'crm.sale.order,%s' % new_id})
            new_ids.append(new_id)
            message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (crm_sale_order.name)
            case.message_post(body=message)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'crm.sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'crm.sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value


    
    _sql_constraints = [     
        ('lead_code_uniq', 'unique (lead_code)',
            'The lead code of the Lead must be unique !'), 
        #TPT - Commented By BalamuruganPurushothaman  on 07/03/2015 -TO AVOID HTIS WARNING                
        #('customer_code_uniq', 'unique (customer_code)',
        #    'The customer code of the Lead must be unique !'),               
    ]
    
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'status':'new',
        'quotation_status':0
        #'lead_code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'lead.code'),
        }
    
crm_lead()

class crm_lead_line(osv.osv):
    _name = "crm.lead.line"
    _columns = {
        'lead_id': fields.many2one('crm.lead','Lead', ondelete='cascade'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),
        'quantity': fields.integer('Quantity'),
        'uom_id': fields.many2one('product.uom','UOM'),
        'application_id': fields.many2one('crm.application','Application'),
        'month': fields.char('Monthly Req. Qty',size=128),
        'year': fields.char('Yearly Req. Qty',size=128),
    }
    
    _defaults = {
        'quantity':1,
    }
    
    def _check_number_month(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        try:
            val = int(obj.month)
            return True
        except ValueError:
            return False
    
    def _check_number_year(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        try:
            val = int(obj.year)
            return True
        except ValueError:
            return False
    
    _constraints = [
        (_check_number_month, 'Monthly Req. Qty is invalid!', ['month']),
        (_check_number_year, 'Yearly Req. Qty is invalid!', ['year']),
    ]
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'uom_id':product.uom_id.id,
                    'product_type':product.tpt_product_type or False,
                    #'application_id':product.application_id or False,
                    }
        return {'value': vals}
    
    def onchange_month(self, cr, uid, ids, month=False, context=None):
        if month:
            try:
                val = int(month)
                return True
            except ValueError:
                raise osv.except_osv(_('Error!'),_("Monthly Req. Qty is invalid!"))
        return True
    
    def onchange_year(self, cr, uid, ids, year=False, context=None):
        if year:
            try:
                val = int(year)
                return True
            except ValueError:
                raise osv.except_osv(_('Error!'),_("Yearly Req. Qty is invalid!"))
        return True
crm_lead_line()

class crm_lead_history(osv.osv):
    _name = "crm.lead.history"
    _columns = {
        'lead_id': fields.many2one('crm.lead','Lead', ondelete='cascade'),
        'status': fields.selection([('new','New'),('opportunity', 'Opportunity'),('quotation', 'Quotation'),
                                    ('awaiting_qc_results','Awaiting QC Results'),('qc_test_completed', 'QC Test Completed'),('sample_received', 'Sample Received'),
                                    ('sample_request','Sample Request'),('awaiting_for_sample_acceptance', 'Awaiting for Sample Acceptance'),('sample_matched', 'Sample Matched'),
                                    ('sample_mismatched','Sample Mismatched'),('cancelled', 'Cancelled'),('won', 'Won'),('closed', 'Closed')],string='Lead Status', size=128,readonly=True),
        'date': fields.datetime('Date'),
    }
    
    _defaults = {
        'date':lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
crm_lead_history()

class crm_sample_request(osv.osv):
    _name = "crm.sample.request"
    _order = "create_date desc"
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(crm_sample_request, self).create(cr, user, vals, context)
        sample_request_id = self.browse(cr, user, new_id)
        self.pool.get('crm.lead').write(cr, user, [sample_request_id.lead_id.id], {'status':'sample_request'}, context=context)
        self.pool.get('crm.lead.history').create(cr, user,{'lead_id':sample_request_id.lead_id.id,'status':'sample_request'}, context=context)
        return new_id
    
    def onchange_lead_id(self, cr, uid, ids,lead_id=False, context=None):
        res = {'value':{
                      'sample_request_line':[],
                      }
               }
        if lead_id:
            lead = self.pool.get('crm.lead').browse(cr, uid, lead_id)
            sample_request_line = []
            for line in lead.lead_line:
                sample_request_line.append({
                          'product_id': line.product_id.id,
                          'product_type':line.product_type,
                          'application_id':line.application_id.id,
                          'quantity':line.quantity,
                          'uom_id': line.uom_id.id,
                    })
        res['value'].update({
                    'sample_request_line': sample_request_line,
        })
        return res
    
    _columns = {
        'name': fields.char('Document No',size=256, required=True,readonly=True),
        'lead_id': fields.many2one('crm.lead','Lead'),
        'subject': fields.char('Subject',size=256),
#         'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type',required=True),
        'description': fields.text('Description'),
        'sample_required':fields.boolean('Sample Required'),
        'sample_request_line': fields.one2many('crm.sample.request.line','sample_request_id','Product Line'),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
    }
    _sql_constraints = [
        ('lead_id_uniq', 'unique (lead_id)', 'The Lead must be unique !'),
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name'], context)
 
        for record in reads:
            name = record['name']
            res.append((record['id'], name))
        return res
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('sample_sending_request'):
            sql = '''
                SELECT sample_request_id FROM crm_sample_sending where sample_request_id is not null
            '''
            cr.execute(sql)
            sample_sending_request_ids = [row[0] for row in cr.fetchall()]
            sample_request_ids = self.search(cr, uid, [('id','not in',sample_sending_request_ids)])
            if context.get('lead_id'):
                sample_request_ids.append(context.get('sample_request_id'))
            args += [('id','in',sample_request_ids)]
        return super(crm_sample_request, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
crm_sample_request()
class crm_sample_request_line(osv.osv):
    _name = "crm.sample.request.line"
    _columns = {
        'sample_request_id': fields.many2one('crm.sample.request','Sample Request', ondelete='cascade'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'quantity': fields.integer('Quantity',required=True),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type',required=True),
        'uom_id': fields.many2one('product.uom','UOM'),
        'application_id': fields.many2one('crm.application','Application'),
            }
    _defaults = {
        'quantity':1,
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'uom_id':product.uom_id.id}
        return {'value': vals}
    
crm_sample_request_line()

class crm_sample_sending (osv.osv):
    _name = "crm.sample.sending"
    _order = "create_date desc"
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(crm_sample_sending, self).create(cr, user, vals, context)
        sample_sending = self.pool.get('crm.sample.sending').browse(cr, user, new_id)
        self.write(cr,user,new_id,{'lead_id':sample_sending.sample_request_id.lead_id.id})
        return new_id
    
    def onchange_sample_request_id(self, cr, uid, ids,sample_request_id=False, context=None):
        res = {'value':{
                      'lead_id':False,  
                      'sample_sending_line':[],
                      }
               }
        if sample_request_id:
            sample_request = self.pool.get('crm.sample.request').browse(cr, uid, sample_request_id)
            sample_sending_line = []
            for line in sample_request.sample_request_line:
                sample_sending_line.append({
                          'product_id': line.product_id.id,
                          'quantity':line.quantity,
                          'product_type':line.product_type,
                          'uom_id': line.uom_id.id,
                          'application_id':line.application_id.id,
                    })
            res['value'].update({
                        'lead_id':sample_request.lead_id.id,
                        'sample_sending_line': sample_sending_line,
            })
        return res
    
    _columns = {
        'name': fields.char('Document No',size=256, required=True,readonly=True),
        'sample_request_id':fields.many2one('crm.sample.request','Sample Request No',required=True),
        'lead_id': fields.many2one('crm.lead','Lead'),
        'application_id': fields.many2one('crm.application','Application'),
        'odour':fields.selection([('odour','Odour'),('odour_less','Odour Less')],'Odour'),
        'texture': fields.char('Texture'),
        'color_in_oil': fields.char('Color in Oil'),
        'reducing_power': fields.char('Reducing Power'),
        'volatile_matter': fields.float('Volatile Matter, % by mass'),
        'purity_as_tio2': fields.float('Purity as TiO2, % by mass'),
        'matter_soluble': fields.float('Matter soluble in Water, % by mass'),
        'residue': fields.float('Residue on 45 micron IS sieve, % by mass'),
        'ph_of_pigment_slurry': fields.float('pH of pigment slurry'),
        'oil_absorption': fields.float('Oil absorption, % by mass'),
        'sample_sending_line': fields.one2many('crm.sample.sending.line','sample_sending_id','Product Line'),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
    }
    _sql_constraints = [
        ('sample_request_id_uniq', 'unique (sample_request_id)', 'The Sample Request No must be unique !'),
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name'], context)
 
        for record in reads:
            name = record['name']
            res.append((record['id'], name))
        return res
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('sample_invoice_sending'):
            sql = '''
                SELECT sample_sending_id FROM crm_sample_invoice where sample_sending_id is not null
            '''
            cr.execute(sql)
            sample_invoice_sending_ids = [row[0] for row in cr.fetchall()]
            sample_sending_ids = self.search(cr, uid, [('id','not in',sample_invoice_sending_ids)])
            if context.get('sample_sending_id'):
                sample_sending_ids.append(context.get('sample_sending_id'))
            args += [('id','in',sample_sending_ids)]
        return super(crm_sample_sending, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    
#     def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
#         if not context: context = {}
#         res = super(crm_sample_sending, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
#         sample_request_ids = self.pool.get('crm.sample.request').search(cr, uid, [], context=context)
#         cr.execute("SELECT sample_request_id FROM crm_sample_sending")
#         configured_cmp = [r[0] for r in cr.fetchall()]
#         unconfigured_cmp = list(set(sample_request_ids)-set(configured_cmp))
#         for field in res['fields']:
#             if field == 'sample_request_id':
#                 res['fields'][field]['domain'] = [('id','in',unconfigured_cmp)]
#         return res
crm_sample_sending()
class crm_sample_sending_line(osv.osv):
    _name = "crm.sample.sending.line"
    _columns = {
        'sample_sending_id': fields.many2one('crm.sample.sending','Sample Sending', ondelete='cascade'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'quantity': fields.integer('Quantity',required=True),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type',required=True),
        'uom_id': fields.many2one('product.uom','UOM'),
        'application_id': fields.many2one('crm.application','Application'),
            }
    _defaults = {
        'quantity':1,
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'uom_id':product.uom_id.id}
        return {'value': vals}
crm_sample_sending_line()



class crm_sample_application(osv.osv):
    _name = "crm.sample.application"
    _columns = {
        'code': fields.char('Code', size=128,required=True),
        'name': fields.char('Name', size=128,required=True),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !'),
    ]
crm_sample_application()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
