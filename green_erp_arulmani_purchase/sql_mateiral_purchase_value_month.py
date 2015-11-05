# -*- coding: utf-8 -*-
# #############################################################################
# 
# #############################################################################
import tools
from osv import fields, osv
from tools.translate import _
import sys
import os
import logging
_logger = logging.getLogger(__name__)

class sql_mateiral_purchase_value_month(osv.osv):
    _name = "sql.mateiral.purchase.value.month"
    _auto = False
    
    #For reports
    def get_line(self, cr, start_year, end_year, category_id, product_ids,avg_value):
        query = '''
            select * from fin_mateiral_purchase_value_month_report(%s,%s,%s,'%s','%s');
        ''' %(start_year, end_year, category_id, product_ids,avg_value)
        cr.execute(query)
        return cr.dictfetchall()
    
    def init(self, cr):
        #TPT-Commented By BalamuruganPurushothaman - On 05/11/2015 - Due to Error while Upgrading Prod Server
        #=======================================================================
        # self.fin_mateiral_purchase_value_month_data(cr)
        # self.fin_mateiral_purchase_value_month_report(cr)
        # cr.commit() 
        #=======================================================================
        return True

    def fin_mateiral_purchase_value_month_data(self, cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_mateiral_purchase_value_month_data')")
#         res = cr.fetchone()
#         if res and res[0]:       
        cr.execute('''delete from pg_type where typname = 'fin_mateiral_purchase_value_month_data';
                        delete from pg_class where relname='fin_mateiral_purchase_value_month_data';
                        commit;''')
        sql = '''
        CREATE TYPE fin_mateiral_purchase_value_month_data AS
           (product_name character varying(1024),
            product_code character varying(100),
            m_4 numeric,
            m_5 numeric,
            m_6 numeric,
            m_7 numeric,
            m_8 numeric,
            m_9 numeric,
            m_10 numeric,
            m_11 numeric,
            m_12 numeric,
            m_1 numeric,
            m_2 numeric,
            m_3 numeric,
            avg numeric);
        ALTER TYPE fin_mateiral_purchase_value_month_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_mateiral_purchase_value_month_report(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_mateiral_purchase_value_month_report(integer, integer, integer, text, character varying) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_mateiral_purchase_value_month_report(integer, integer, integer, text, character varying)
          RETURNS SETOF fin_mateiral_purchase_value_month_data AS
        $BODY$
        DECLARE
            rec        record;
            rec3        record;
            rec2        integer;
            bal_data    fin_mateiral_purchase_value_month_data%ROWTYPE;
            num      numeric=0;
            total    numeric=0;
            m_4        numeric=0;
            m_5     numeric=0;
            m_6     numeric=0;
            m_7     numeric=0;
            m_8     numeric=0;
            m_9     numeric=0;
            m_10     numeric=0;
            m_11     numeric=0;
            m_12     numeric=0;
            m_1     numeric=0;
            m_2     numeric=0;
            m_3     numeric=0;
            avg     numeric=0;
        BEGIN
            if $4 = '' then
                for rec in execute '
                    select product_product.id as product_id, product_product.default_code as product_code, product_product.name_template as product_name
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = $1) 
                        and product_product.product_tmpl_id = product_template.id
                    'using $3
                loop
                    for rec2 in 1..12
                    loop
                        if rec2 not in (1,2,3) then
                            for rec3 in execute '
                                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                                    from purchase_order_line 
                                    where product_id = $1 and order_id in (select id from purchase_order where EXTRACT(year from date_order) = $2
                                    and EXTRACT(month from date_order) = $3 and state in (''md'',''approved'',''done'',''except_picking'',''except_invoice''))
                                'using rec.product_id, $1, rec2
                            loop
                                if coalesce(rec3.value1, 0) <>0 then
                                    num = num+1;
                                    total = total+coalesce(rec3.value1, 0);
                                end if;
                                if rec2=4 then
                                    m_4 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=5 then
                                    m_5 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=6 then
                                    m_6 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=7 then
                                    m_7 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=8 then
                                    m_8 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=9 then
                                    m_9 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=10 then
                                    m_10 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=11 then
                                    m_11 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=12 then
                                    m_12 = coalesce(rec3.value1, 0);
                                end if;
                            end loop;
                        else
                            for rec3 in execute '
                                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                                    from purchase_order_line 
                                    where product_id = $1 and order_id in (select id from purchase_order where EXTRACT(year from date_order) = $2
                                    and EXTRACT(month from date_order) = $3 and  state in (''md'',''approved'',''done'',''except_picking'',''except_invoice''))
                                'using rec.product_id, $2, rec2
                            loop
                                if coalesce(rec3.value1, 0) <>0 then
                                    num = num+1;
                                    total = total+coalesce(rec3.value1, 0);
                                end if;
                                if rec2=1 then
                                    m_1 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=2 then
                                    m_2 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=3 then
                                    m_3 = coalesce(rec3.value1, 0);
                                end if;
                            end loop;
                        end if;
                    end loop;
                    if num <> 0 then
                        avg = total/num::float;
                    end if;
                    if $5 = '' then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;   
                    end if;
                    if $5='0' and total = 0 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = 0;
                        
                        return next bal_data;
                    end if;
                    if $5='1' and avg>=1 and avg<=5000 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    if $5='5001' and avg>=5001 and avg<=10000 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    if $5='all' then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    m_4=0;
                    m_5=0;
                    m_6=0;
                    m_7=0;
                    m_8=0;
                    m_9=0;
                    m_10=0;
                    m_11=0;
                    m_12=0;
                    m_1=0;
                    m_2=0;
                    m_3=0;
                    num=0;
                    total=0;
                    avg=0;
                end loop;
            else
                for rec in execute '
                    select product_product.id as product_id, product_product.default_code as product_code, product_product.name_template as product_name
                        from product_product 
                        where id in (select regexp_split_to_table($1, '', '')::integer)
                    'using $4
                loop
                    for rec2 in 1..12
                    loop
                        if rec2 not in (1,2,3) then
                            for rec3 in execute '
                                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                                    from purchase_order_line 
                                    where product_id = $1 and order_id in (select id from purchase_order where EXTRACT(year from date_order) = $2
                                    and EXTRACT(month from date_order) = $3 and state in (''md'',''approved'',''done'',''except_picking'',''except_invoice''))
                                'using rec.product_id, $1, rec2
                            loop
                                if coalesce(rec3.value1, 0) <>0 then
                                    num = num+1;
                                    total = total+coalesce(rec3.value1, 0);
                                end if;
                                if rec2=4 then
                                    m_4 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=5 then
                                    m_5 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=6 then
                                    m_6 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=7 then
                                    m_7 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=8 then
                                    m_8 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=9 then
                                    m_9 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=10 then
                                    m_10 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=11 then
                                    m_11 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=12 then
                                    m_12 = coalesce(rec3.value1, 0);
                                end if;
                            end loop;
                        else
                            for rec3 in execute '
                                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                                    from purchase_order_line 
                                    where product_id = $1 and order_id in (select id from purchase_order where EXTRACT(year from date_order) = $2
                                    and EXTRACT(month from date_order) = $3 and  state in (''md'',''approved'',''done'',''except_picking'',''except_invoice''))
                                'using rec.product_id, $2, rec2
                            loop
                                if coalesce(rec3.value1, 0) <>0 then
                                    num = num+1;
                                    total = total+coalesce(rec3.value1, 0);
                                end if;
                                if rec2=1 then
                                    m_1 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=2 then
                                    m_2 = coalesce(rec3.value1, 0);
                                end if;
                                if rec2=3 then
                                    m_3 = coalesce(rec3.value1, 0);
                                end if;
                            end loop;
                        end if;
                    end loop;
                    if num <> 0 then
                        avg = total/num::float;
                    end if;
                    if $5 = '' then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;   
                    end if;
                    if $5='0' and total = 0 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = 0;
                        
                        return next bal_data;
                    end if;
                    if $5='1' and avg>=1 and avg<=5000 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    if $5='5001' and avg>=5001 and avg<=10000 then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    if $5='all' then
                        bal_data.product_name = rec.product_name;
                        bal_data.product_code = rec.product_code;
                        bal_data.m_1 = m_1;
                        bal_data.m_2 = m_2;
                        bal_data.m_3 = m_3;
                        bal_data.m_4 = m_4;
                        bal_data.m_5 = m_5;
                        bal_data.m_6 = m_6;
                        bal_data.m_7 = m_7;
                        bal_data.m_8 = m_8;
                        bal_data.m_9 = m_9;
                        bal_data.m_10 = m_10;
                        bal_data.m_11 = m_11;
                        bal_data.m_12 = m_12;
                        bal_data.avg = avg;
                        
                        return next bal_data;
                    end if;
                    m_4=0;
                    m_5=0;
                    m_6=0;
                    m_7=0;
                    m_8=0;
                    m_9=0;
                    m_10=0;
                    m_11=0;
                    m_12=0;
                    m_1=0;
                    m_2=0;
                    m_3=0;
                    num=0;
                    total=0;
                    avg=0;
                end loop;
            end if;
            
            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 90000;
        ALTER FUNCTION fin_mateiral_purchase_value_month_report(integer, integer, integer, text, character varying)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
sql_mateiral_purchase_value_month()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
