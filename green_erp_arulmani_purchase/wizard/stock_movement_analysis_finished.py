# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
import locale
from global_utility import tpt_shared_component
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

""" 
TPT - By P.Vinothkumar  - on 28/06/2016
Stock Movement Analysis-Finished Report
"""
class stock_movement_analysis_finished(osv.osv):
    _name = "stock.movement.analysis.finished"
    _columns = {    
                'product_id': fields.many2one('product.product', 'Product',cate_name='finish',required = True),
                'date_from':fields.date('Date From',required = True),
                'date_from_title':fields.char('Date From'),
                'date_to':fields.date('Date To',required = True),
                'date_to_title':fields.char('Date To'),
                'product_name':fields.char('Product',size=1024),
                'product_name_title':fields.char('Product',size=1024),
                'name':fields.char('Stock Movement Analysis',size=1024,readonly=True),
                'movement_line':fields.one2many('stock.movement.analysis.line.finished','movement_id','Stock Movement Finished'),
                }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.form.movement.analysis.finished'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_finished_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.form.movement.analysis.finished'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_finished_pdf', 'datas': datas}
    
stock_movement_analysis_finished()

class stock_movement_analysis_line_finished(osv.osv):
    _name = "stock.movement.analysis.line.finished"
    _columns = {    
        'movement_id': fields.many2one('stock.movement.analysis.finished', 'Stock Movement Finished', ondelete='cascade'),
        'month': fields.char('Month', size = 1024),
        'year': fields.char('Year', size = 1024),
        'open_stock': fields.float('Opening Stock',digits=(16,3)),
        'prod_qty': fields.float('Production Quantity',digits=(16,3)),
        'trans_qty': fields.float('Transfer to Other Location',digits=(16,3)),
        'receive_qty': fields.float('Receive from other location',digits=(16,3)),
        'sold_qty': fields.float('Sales',digits=(16,3)),
        'closing_stock_calc': fields.float('Closing stock(as per calculation)',digits=(16,3)),
        'closing_stock_onhand': fields.float('Closing stock(as per onhand)',digits=(16,3)),
        'difference' : fields.float('Difference',digits=(16,3)),
                }
stock_movement_analysis_line_finished() 

class stock_movement_finished(osv.osv):
    _name = "stock.movement.finished"
    _columns = {    
        'product_id': fields.many2one('product.product', 'Product',required = True),
        'date_from':fields.date('Date From',required = True),
        'date_to':fields.date('Date To',required = True),
        }
    

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        movement_obj = self.pool.get('stock.movement.analysis.finished')
        movement = self.browse(cr, uid, ids[0])
        def get_amount(amt):       
            locale.setlocale(locale.LC_NUMERIC, "en_IN")
            inr_comma_format = locale.format("%.3f", amt, grouping=True)
            return inr_comma_format
#         def opening_stock(product_id, year, month):
#             location_id=13
#             if product_id== 2: 
#                 location_id=25 #FSH
#             elif product_id== 3: 
#                 location_id=26 #Ferric Sulphate
#             elif product_id== 4: 
#                 location_id=13  #TIO2
#             elif product_id== 5: 
#                 location_id=27  #Effluent 
#             elif product_id==6: 
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material   
#             elif product_id==7:  
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material      
#             elif product_id==9:  
#                 location_id=13  #TIO2 
#             elif product_id==10745:  
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material 
#             elif product_id==12906:  
#                 location_id=24  #Other        
#             elif product_id==13030:  
#                 location_id=24  #Other
#             sql='''
#              select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from
#             (select st.product_qty as product_qty, st.date
#                 from stock_move st
#                 where st.state='done' and st.product_id=%(product_id)s and st.location_dest_id=%(location_id)s 
#                 and st.location_dest_id != st.location_id
#              union all
#              select st.product_qty*-1 as product_qty, st.date
#                 from stock_move st
#                 where st.state='done'
#                         and st.product_id=%(product_id)s
#                             and location_id=%(location_id)s
#                             and location_dest_id != location_id
#             )foo
#             where EXTRACT(month FROM foo.date)<%(month)s and EXTRACT(Year FROM foo.date)=%(year)s
#              '''%{
#                 'location_id':location_id,
#                 'product_id':product_id,
#                 'year':year,
#                 'month':month
#                 } 
#             cr.execute(sql)
#             #print sql
#             openingstock = cr.fetchone()[0]
#             return openingstock

        # Added by P.vinothkumar on 01/07/2016 for fixed opening stock value. 
        def opening_stock(product_id, default_code):
            location = tpt_shared_component.warehouse_module() 
            location_id = location.get_finished_location(default_code) 
            # Comment by P.vinothkumar on 02/07/2016 find location using globla class
#             location_id=13
#             if product_id== 2: 
#                 location_id=25 #FSH
#             elif product_id== 3: 
#                 location_id=26 #Ferric Sulphate
#             elif product_id== 4: 
#                 location_id=13  #TIO2
#             elif product_id== 5: 
#                 location_id=27  #Effluent 
#             elif product_id==6: 
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material   
#             elif product_id==7:  
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material      
#             elif product_id==9:  
#                 location_id=13  #TIO2 
#             elif product_id==10745:  
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material 
#             elif product_id==12906:  
#                 location_id=24  #Other        
#             elif product_id==13030:  
#                 location_id=24  #Other
            sql='''
            select
            sum(st.product_qty) as product_qty
            from stock_move st
            where st.state='done' and st.product_id=%s and st.location_dest_id=%s 
            and st.location_dest_id != st.location_id
            and name = 'INV:Update'
            and EXTRACT(month FROM st.date)<4 and EXTRACT(Year FROM st.date)=2015'''%(product_id,location_id)
            cr.execute(sql)
            stock_opening = cr.fetchone()[0]
            return stock_opening or 0.00
        
        def sale_qty(product_id, date):
            sql='''
                select sum(ail.quantity) from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ail.product_id=%s and ai.date_invoice < '%s'
               
                '''%(product_id,date)
            cr.execute(sql)
            sales_qty=cr.fetchone()[0]
            return sales_qty or 0.00
        
        def production_qty(product_id, date):
            sql='''
                Select  sum(product_qty) as productionQty 
                from mrp_production mrp 
                Inner join product_product p on (p.id=mrp.product_id and p.id not in (7))  
                where date_planned < '%s' 
                and p.id =(%s)'''%(date,product_id)
            cr.execute(sql)
            prod_qty=cr.fetchone()[0]    
            return prod_qty or 0.00
        
        def total_received_qty(product_id, date):
            sql='''
                select sum(a.AdjustedQty) as adjustedqty 
                from (
                select p.id as ProductID,si.id as ReferenceID, si.name as stockAdjustmentName, si.date as StockAdjustmentDate,
                EXTRACT(month FROM si.date) transactionmonth, EXTRACT(year FROM si.date) transactionyear,
                p.name_template as productName, spl.name as SystemBatchNo,spl.phy_batch_no as PhysicalBatchNo, 
                product_qty as AdjustedQty,'Increased to 1 MT' as adjustmenttype from stock_inventory_line sil 
                Inner join stock_production_lot spl on (spl.id=sil.prod_lot_id)
                Inner join product_product p on (p.id=sil.product_id)
                Inner join stock_inventory si on (si.id=sil.inventory_id)
                where sil.product_id=4 and spl.name like '%s(M)%s' and 
                 si.date < '%s'
                )a 
                --group by a.ProductID, a.productName, a.transactionyear, a.transactionmonth
                --order by a.productName'''%('%', '%', date)
            cr.execute(sql)
            received_qty=cr.fetchone()
            if received_qty:
                received_qty = received_qty[0]
            return received_qty or 0.00 
        
        
        def monthly_received_qty(product_id,month,year):
            receive_qty = 0.0
            sql='''
                select sum(a.AdjustedQty) as adjustedqty 
                from (
                select p.id as ProductID,si.id as ReferenceID, si.name as stockAdjustmentName, si.date as StockAdjustmentDate,
                EXTRACT(month FROM si.date) transactionmonth, EXTRACT(year FROM si.date) transactionyear,
                p.name_template as productName, spl.name as SystemBatchNo,spl.phy_batch_no as PhysicalBatchNo, 
                product_qty as AdjustedQty,'Increased to 1 MT' as adjustmenttype from stock_inventory_line sil 
                Inner join stock_production_lot spl on (spl.id=sil.prod_lot_id)
                Inner join product_product p on (p.id=sil.product_id)
                Inner join stock_inventory si on (si.id=sil.inventory_id)
                where sil.product_id=4 and spl.name like '%s(M)%s' and 
                 EXTRACT(month FROM si.date)=%s and EXTRACT(Year FROM si.date)=%s
                )a 
                group by a.ProductID, a.productName, a.transactionyear, a.transactionmonth
                order by a.productName
             '''%('%', '%', month, year)
            #print sql
            cr.execute(sql)
            receive_qty = cr.fetchone()
            if receive_qty:
                receive_qty = receive_qty[0]
            return receive_qty or 0.00  
         
        cr.execute('delete from stock_movement_analysis_finished')
        movement_line = []
        sql= '''
            select  a.product_code, a.transactionYear as Yearperiod, a.transactionmonth as monthperiod, a.mon, sum(a.productionQty) as producedqty, 
            sum(a.salesqty) as salesQty from  
            (
            Select p.default_code as product_code,date_planned as transactiondate, product_qty as productionQty, 0 as salesqty,
            EXTRACT(YEAR FROM date_planned) as transactionYear,EXTRACT(month FROM date_planned) as mon, 
            (select to_char((date_planned)::date,'Month')) as TransactionMonth 
            from mrp_production mrp 
            Inner join product_product p on (p.id=mrp.product_id and p.id not in (7))  
            where date_planned >='%(date_from)s' and date_planned <='%(date_to)s'
            and p.id =(%(product_id)s)
            
            union all
            
            select p.default_code as product_code, ai.date_invoice as transactiondate,0 as productionqty, 
            ail.quantity as salesqty,
            EXTRACT(YEAR FROM ai.date_invoice) as transactionYear, EXTRACT(month FROM date_invoice) as mon,(select to_char((ai.date_invoice)::date,'Month')) as transactionmonth
            from account_invoice_line ail
            inner join account_invoice ai on (ai.id=ail.invoice_id and ai.type='out_invoice') 
            Inner join product_product p on (p.id=ail.product_id and p.id not in (7))  
            where ai.date_invoice >='%(date_from)s' and ai.date_invoice <='%(date_to)s' and p.id=(%(product_id)s)
            
            )a 
            group by a.transactionYear, a.mon,a.transactionmonth,a.product_code
            order by a.transactionYear,a.mon
            ''' %{'date_from':movement.date_from,
                  'date_to':movement.date_to,
                  'product_id':movement.product_id.id or False
                    }
        cr.execute(sql)
        #print sql
        #closing_stock_onhand = 0.0
        temp = 0.0
        trans_qty = 0.0
        trans_qty1, trans_qty2 = 0.0, 0.0
        receive_qty1,receive_qty2=0.0, 0.0
        for line in cr.dictfetchall():
            #open_qty = opening_stock(movement.product_id.id,int(line['yearperiod']),int(line['mon']))
            open_date = str(int(line['yearperiod']))+'-'+str(int(line['mon']))+'-'+'01' # To find starting date of every month 
            open_qty = opening_stock(movement.product_id.id, movement.product_id.default_code)
            sales_qty= sale_qty(movement.product_id.id, open_date)
            prod_qty= production_qty(movement.product_id.id, open_date)
            receive_qty1= total_received_qty(movement.product_id.id, open_date)
            receive_qty2=receive_qty1
            trans_qty1 = monthly_received_qty(movement.product_id.id,int(line['mon']),int(line['yearperiod']))
            trans_qty2 = trans_qty1
            if line['product_code']=='M0501010001':
                trans_qty1 = 0.0
                receive_qty1=0.0
            elif line['product_code']=='M0501010008':
                trans_qty2 = 0.0
                trans_qty1 = -trans_qty1
                receive_qty2=0.0
                receive_qty1=-receive_qty1
            else:#FOR FSH
                trans_qty1 = 0.0
                trans_qty2 = 0.0
                receive_qty1=0.0
                receive_qty2=0.0
                
            opening_qty= open_qty+prod_qty+receive_qty1+receive_qty2-sales_qty    
            #closing_qty =  open_qty+line['producedqty']+trans_qty1+trans_qty2 -line['salesqty']  
            closing_qty =  opening_qty+line['producedqty']+trans_qty1+trans_qty2 -line['salesqty']  
            movement_line.append((0,0,{ 
                'month': line['monthperiod'],
                'year': int(line['yearperiod']) or '',
                'open_stock': opening_qty or 0.0,
                'prod_qty': line['producedqty'],
                'trans_qty': trans_qty1 ,
                'receive_qty': trans_qty2 ,
                'sold_qty': line['salesqty'],
                'closing_stock_calc': closing_qty or 0.0,
                'closing_stock_onhand':closing_qty or 0.0,
                'difference' : closing_qty-closing_qty or 0.0,  
            }))
        
        vals = {
                'product_id': movement.product_id and movement.product_id.id or False,
                'date_from':movement.date_from,
                'date_from_title':'Date From: ',
                'date_to':movement.date_to,
                'date_to_title':'Date To: ',
                'product_name':movement.product_id.name,
                'product_name_title':'Product: ',
                'name':'Stock Movement Analysis Finished product',
                'movement_line':movement_line,
                }
                #
        movement_id = movement_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_stock_movement_analysis_finished')
        return {
            'name': 'Stock Movement Analysis - Finished Product',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.movement.analysis.finished',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': movement_id,
                }   
        
        
stock_movement_finished()        
        
        


   
    



