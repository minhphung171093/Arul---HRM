# -*- coding: utf-8 -*-
##############################################################################
#    Written By TPT-BM ON 30/06/2016
#    This will be used for global variables & methods access from any where in the project
##############################################################################
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

class warehouse_module():
    
    def get_warehouse_finish(self):
        
        dict = {}
        locat_obj = self.pool.get('stock.location')
        if line.product_id.default_code in ['M0501010001', 'M0501010008']:
            name = 'TIO2'
        elif line.product_id.default_code=='M0501010002':
            name = 'FSH'
        parent_ids = locat_obj.search(cr, uid, [('name','=',name),('usage','=','internal')])
        
        return True
    
    def get_return_warehouse_finish1(self):
        
        dict = {}
        locat_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        product_obj_finish = product_obj.search(cr, uid, [('cate_name','=','finish')])
        product_obj_finish_ids = product_obj.browse(cr,uid,product_obj_finish)
        for line in product_obj_finish_ids:
            if line.default_code in ['M0501010001', 'M0501010008']:
                name = 'TIO2'
            elif line.product_id.default_code=='M0501010002':
                name = 'FSH'    
            parent_ids = locat_obj.search(cr, uid, [('name','=',name),('usage','=','internal')])
            if parent_ids:
                locat_obj_ids = locat_obj.browse(cr,uid,parent_ids[0])
            dict[line.default_code] = a
        return True

    def get_return_warehouse_finish(self, default_code):
        """ Gets From, To Location in which the given finished product moves for return DO process
            @param default_code: Stock move lines
            @return: The code of the finished product (default_code column in product_product table)
        """
        location_id, location_dest_id = False, False
        if default_code in ['M0501010001', 'M0501010008']:
            location_id = 9 #Partner Locations / Customers
            location_dest_id = 13 #Physical Locations / VVTi Pigments / Store / TIO2
        elif default_code=='M0501010002':
            name = 'FSH'   
            location_id = 9
            location_dest_id = 25 #Physical Locations / VVTi Pigments / Store / FSH
        return location_id, location_dest_id
    
    # Added by P.vinothkumar on 02/07/2016 using this method for stock transfer report-finished products
    def get_finished_location(self,default_code):
        
        location_dest_id = False
        if default_code in ['M0501010001', 'M0501010008']:
            location_dest_id = 13 #Physical Locations / VVTi Pigments / Store / TIO2
        elif default_code=='M0501010002':
            location_dest_id = 25 #Physical Locations / VVTi Pigments / Store / FSH
        elif default_code=='M0501010006':
            location_dest_id =26
        elif default_code=='M0501010003':
            location_dest_id =27  
        elif default_code in ['M0501010004','M0501010005','M0501020028']:
            location_dest_id =23
        elif default_code in ['M0501010009','M0501010010']:
            location_dest_id =24          
        else:
            location_dest_id = 13 
        return location_dest_id
            