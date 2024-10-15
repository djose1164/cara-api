create or replace package buy_order_processing
	procedure add_order(param_supplier_id int, param_salesperson_id int, param_description tinytext, param_date datetime);
	
	procedure add_order_detail(param_buy_order_id int, param_product_id int, param_quantity int);

	procedure update_payment(param_buy_order_id int, param_paid_amount decimal(10, 2));

	function get_order_total(param_buy_order_id int) returns decimal(10, 2);
end;


create or replace package body buy_order_processing
	procedure add_order(
		param_supplier_id int, 
		param_salesperson_id int, 
		param_description tinytext,
		param_date datetime)
	begin
		insert into buy_orders(provider_id, salesperson_id, description, date)
		values(param_supplier_id, param_salesperson_id, param_description, param_date);
	end;
	
	procedure add_order_detail(
		param_buy_order_id int, 
		param_product_id int, 
		param_quantity int)
	begin
		insert into buy_order_details(buy_order_id, product_id, quantity)
		values(param_buy_order_id, param_product_id, param_quantity);
	end;
	
	procedure update_payment(param_buy_order_id int, param_paid_amount decimal(10, 2))
	begin
		declare v_payment_status int;
		declare v_amount_to_pay decimal(10, 2) default get_order_total(param_buy_order_id);
		
		if param_paid_amount = 0 then
			set v_payment_status = 2; -- Credit
		elseif v_amount_to_pay = param_paid_amount then
			set v_payment_status = 1; -- Paid
		else 
			set v_payment_status = 3; -- Partial paid
		end if;
		
		insert into payments(amount_to_pay, paid_amount, payment_status_id)
		values(v_amount_to_pay, param_paid_amount, v_payment_status);
	
		update buy_orders 
		set payment_id = last_insert_id()
		where id = param_buy_order_id;
	end;

	function get_order_total(param_buy_order_id int)
	returns decimal(10, 2)
	begin
		declare v_order_total int default 0;
	
		select sum(ph.price*quantity) into v_order_total 
		from buy_order_details bod
		join price_history ph 
			on ph.product_id = bod.product_id and ph.price_type = 'buy'
		where ph.thru_date is null and bod.buy_order_id = param_buy_order_id;
	
		return v_order_total;
	end;
end;


-- Example of use.
-- call buy_order_processing.add_order(1, 1, 'Insertado desde Stored Procedure!');
-- Set @by_id = last_insert_id();
-- 
-- call buy_order_processing.add_order_detail(@by_id, 1, 5);
-- call buy_order_processing.add_order_detail(@by_id, 2, 3);
-- call buy_order_processing.add_order_detail(@by_id, 3, 7);
-- call buy_order_processing.add_order_detail(@by_id, 4, 8);
-- 
-- call buy_order_processing.update_payment(@by_id, buy_order_processing.get_order_total(@by_id));


