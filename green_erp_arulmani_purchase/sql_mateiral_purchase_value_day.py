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

class sql_mateiral_purchase_value_day(osv.osv):
    _name = "sql.mateiral.purchase.value.day"
    _auto = False
    
    #For reports
    def get_line(self, cr, year, month, category_id, product_ids,avg_value):
        query = '''
            select * from fin_mateiral_purchase_value_day_report(%s,%s,%s,'%s','%s');
        ''' %(year, month, category_id, product_ids,avg_value)
        cr.execute(query)
        return cr.dictfetchall()
    
    def init(self, cr):
        self.fin_mateiral_purchase_value_day_data(cr)
        self.fin_mateiral_purchase_value_day_report(cr) 
        self.get_day_of_month(cr)
        #TPT-Commented By BalamuruganPurushothaman - On 05/11/2015 - Due to Error while Upgrading Prod Server
        #cr.commit()
        return True

    def fin_mateiral_purchase_value_day_data(self, cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_mateiral_purchase_value_month_data')")
#         res = cr.fetchone()
#         if res and res[0]:
        #TPT-Commented By BalamuruganPurushothaman - On 05/11/2015 - Due to Error while Upgrading Prod Server
        #=======================================================================
        # cr.execute('''delete from pg_type where typname = 'fin_mateiral_purchase_value_day_data';
        #                 delete from pg_class where relname='fin_mateiral_purchase_value_day_data';
        #                 commit;''')
        #=======================================================================
        sql = '''
        CREATE TYPE fin_mateiral_purchase_value_day_data AS
           (product_name character varying(1024),
            product_code character varying(100),
            m_1 numeric,
            m_2 numeric,
            m_3 numeric,
            m_4 numeric,
            m_5 numeric,
            m_6 numeric,
            m_7 numeric,
            m_8 numeric,
            m_9 numeric,
            m_10 numeric,
            m_11 numeric,
            m_12 numeric,
            m_13 numeric,
            m_14 numeric,
            m_15 numeric,
            m_16 numeric,
            m_17 numeric,
            m_18 numeric,
            m_19 numeric,
            m_20 numeric,
            m_21 numeric,
            m_22 numeric,
            m_23 numeric,
            m_24 numeric,
            m_25 numeric,
            m_26 numeric,
            m_27 numeric,
            m_28 numeric,
            m_29 numeric,
            m_30 numeric,
            m_31 numeric,
            avg numeric);
        ALTER TYPE fin_mateiral_purchase_value_day_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def get_day_of_month(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_balance_cr')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS get_day_of_month(integer, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION get_day_of_month(integer, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            days    integer = 0;
        BEGIN
            if $2 = 2 and ($1%4 = 0) and ($1%100 <> 0) or ($1%400 = 0) then
                days = 29;
            end if;
            if $2 = 2 and not (($1%4 = 0) and ($1%100 <> 0) or ($1%400 = 0)) then
                days = 28;
            end if;
            if $2 = 1 then
                days = 31;
            end if;
            if $2 = 3 then
                days = 31;
            end if;
            if $2 = 4 then
                days = 30;
            end if;
            if $2 = 5 then
                days = 31;
            end if;
            if $2 = 6 then
                days = 30;
            end if;
            if $2 = 7 then
                days = 31;
            end if;
            if $2 = 8 then
                days = 31;
            end if;
            if $2 = 9 then
                days = 30;
            end if;
            if $2 = 10 then
                days = 31;
            end if;
            if $2 = 11 then
                days = 30;
            end if;
            if $2 = 12 then
                days = 31;
            end if;
        
            return days;
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION get_day_of_month(integer, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_mateiral_purchase_value_day_report(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_mateiral_purchase_value_day_report(integer, integer, integer, text, character varying) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_mateiral_purchase_value_day_report(integer, integer, integer, text, character varying)
          RETURNS SETOF fin_mateiral_purchase_value_day_data AS
        $BODY$
        DECLARE
            rec        record;
            rec3        record;
            rec2        integer;
            bal_data    fin_mateiral_purchase_value_day_data%ROWTYPE;
            days        integer;
            num      numeric=0;
            total    numeric=0;
            m_1     numeric=0;
            m_2     numeric=0;
            m_3     numeric=0;
            m_4        numeric=0;
            m_5     numeric=0;
            m_6     numeric=0;
            m_7     numeric=0;
            m_8     numeric=0;
            m_9     numeric=0;
            m_10     numeric=0;
            m_11     numeric=0;
            m_12     numeric=0;
            m_13     numeric=0;
            m_14     numeric=0;
            m_15     numeric=0;
            m_16     numeric=0;
            m_17     numeric=0;
            m_18     numeric=0;
            m_19     numeric=0;
            m_20     numeric=0;
            m_21     numeric=0;
            m_22     numeric=0;
            m_23     numeric=0;
            m_24     numeric=0;
            m_25     numeric=0;
            m_26     numeric=0;
            m_27     numeric=0;
            m_28     numeric=0;
            m_29     numeric=0;
            m_30     numeric=0;
            m_31     numeric=0;
            avg     numeric=0;
        BEGIN
            days = get_day_of_month($1,$2);
            if $4 = '' then
                for rec in execute '
                    select product_product.id as product_id, product_product.default_code as product_code, product_product.name_template as product_name
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = $1) 
                        and product_product.product_tmpl_id = product_template.id
                    'using $3
                loop
                    for rec2 in 1..days
                    loop
                        for rec3 in execute '
                            select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                                from purchase_order_line 
                                where product_id = $1 and order_id in (select id from purchase_order where EXTRACT(year from date_order) = $2
                                and EXTRACT(month from date_order) = $3 and EXTRACT(day from date_order) = $4 and state in (''md'',''approved'',''done'',''except_picking'',''except_invoice''))
                            'using rec.product_id, $1, $2, rec2
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
                            if rec2=13 then
                                m_13 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=14 then
                                m_14 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=15 then
                                m_15 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=16 then
                                m_16 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=17 then
                                m_17 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=18 then
                                m_19 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=20 then
                                m_20 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=21 then
                                m_21 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=22 then
                                m_22 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=23 then
                                m_23 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=24 then
                                m_24 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=25 then
                                m_25 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=26 then
                                m_26 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=27 then
                                m_27 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=28 then
                                m_28 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=29 and days>28 then
                                m_29 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=30 and days>29 then
                                m_30 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=31 and days>30 then
                                m_31 = coalesce(rec3.value1, 0);
                            end if;
                        end loop;
                    end loop;
                    if num <> 0 then
                        avg = total/num::float;
                    end if;
                    if $5 = '' or $5='all' then
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                    m_13=0;
                    m_14=0;
                    m_15=0;
                    m_16=0;
                    m_17=0;
                    m_18=0;
                    m_19=0;
                    m_20=0;
                    m_21=0;
                    m_22=0;
                    m_23=0;
                    m_24=0;
                    m_25=0;
                    m_26=0;
                    m_27=0;
                    m_28=0;
                    m_29=0;
                    m_30=0;
                    m_31=0;
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
                    for rec2 in 1..days
                    loop
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
                            if rec2=13 then
                                m_13 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=14 then
                                m_14 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=15 then
                                m_15 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=16 then
                                m_16 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=17 then
                                m_17 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=18 then
                                m_19 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=20 then
                                m_20 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=21 then
                                m_21 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=22 then
                                m_22 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=23 then
                                m_23 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=24 then
                                m_24 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=25 then
                                m_25 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=26 then
                                m_26 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=27 then
                                m_27 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=28 then
                                m_28 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=29 and days>28 then
                                m_29 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=30 and days>29 then
                                m_30 = coalesce(rec3.value1, 0);
                            end if;
                            if rec2=31 and days>30 then
                                m_31 = coalesce(rec3.value1, 0);
                            end if;
                        end loop;
                    end loop;
                    if num <> 0 then
                        avg = total/num::float;
                    end if;
                    if $5 = '' or $5 = 'all' then
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                        bal_data.m_13 = m_13;
                        bal_data.m_14 = m_14;
                        bal_data.m_15 = m_15;
                        bal_data.m_16 = m_16;
                        bal_data.m_17 = m_17;
                        bal_data.m_18 = m_18;
                        bal_data.m_19 = m_19;
                        bal_data.m_20 = m_20;
                        bal_data.m_21 = m_21;
                        bal_data.m_22 = m_22;
                        bal_data.m_23 = m_23;
                        bal_data.m_24 = m_24;
                        bal_data.m_25 = m_25;
                        bal_data.m_26 = m_26;
                        bal_data.m_27 = m_27;
                        bal_data.m_28 = m_28;
                        bal_data.m_29 = m_29;
                        bal_data.m_30 = m_30;
                        bal_data.m_31 = m_31;
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
                    m_13=0;
                    m_14=0;
                    m_15=0;
                    m_16=0;
                    m_17=0;
                    m_18=0;
                    m_19=0;
                    m_20=0;
                    m_21=0;
                    m_22=0;
                    m_23=0;
                    m_24=0;
                    m_25=0;
                    m_26=0;
                    m_27=0;
                    m_28=0;
                    m_29=0;
                    m_30=0;
                    m_31=0;
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
        ALTER FUNCTION fin_mateiral_purchase_value_day_report(integer, integer, integer, text, character varying)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
sql_mateiral_purchase_value_day()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
