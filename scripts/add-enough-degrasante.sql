-- Agrega suficientes degrasantes.
-- Rason: Se vendio un degrasante, y el sistema no cuenta con el stock real en almacen.

set @degrasante_cantidad = 5;
set @total_to_pay = 0;

select id into @degrasante_id from products where name = 'Degrasante';

select buy_price*@degrasante_cantidad into @total_to_pay 
from products 
where name = 'Degrasante';


insert into payments(amount_to_pay, paid_amount, payment_status_id)
values(@total_to_pay, @total_to_pay, 1);


insert into buy_orders(date, provider_id, payment_id, description, salesperson_id)
values(now(), 1, (select id from payments p order by 1 desc limit 1), 'Agrega suficientes degrasantes', 1);

insert into buy_order_details(product_id, quantity, buy_order_id)
values((select id from products where name = 'Degrasante'), @degrasante_cantidad, (select id from buy_orders order by 1 desc limit 1));

update inventory i 
set quantity_available = @degrasante_cantidad
where product_id = @degrasante_id and salesperson_id = 1;


