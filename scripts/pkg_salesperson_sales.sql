create or replace package sales
	procedure add_sale(param_customer_id int, param_order_id int);
	
	procedure add_sale_item(param_sale_id int, param_product_id int, param_quantity int);

	procedure update_sale_total(param_sale_id int);
	
	procedure get_sale(p_sale_id int);
end;

create or replace package body sales
	procedure add_sale(param_customer_id int, param_order_id int)
	begin
		insert into sale(customer_id, order_id)
		values(param_customer_id, param_order_id);
	end;
	
	procedure add_sale_item(
		param_sale_id int, 
		param_product_id int, 
		param_quantity int)
	begin
    	declare v_unit_price decimal(6, 2) default 0;
        
        select price into v_unit_price
        from price_history ph 
        where ph.price_type = 'sell' and ph.product_id = param_product_id and ph.thru_date is null;

		insert into sale_item(sale_id, product_id, quantity, unit_price)
		values(param_sale_id, param_product_id, param_quantity, v_unit_price);
	end;
	
	-- Set the total_amount based on the items linked to the sale.
	procedure update_sale_total(param_sale_id int)
	begin 
		update sale
		set total_amount = (select sum(quantity*unit_price) 
							from sale_item si 
							where si.sale_id = param_sale_id)
		where id = param_sale_id;
	end;
	
	procedure get_sale(p_sale_id int)
	begin
    	select *
    	from sale s 
    	where s.id = p_sale_id;
    end;
end;

call sales.add_sale_item(4, 1, 3);
call sales.update_sale_total(4);