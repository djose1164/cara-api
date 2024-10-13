-- CARA API - 0.19.0
-- AUTHOR: Daniel Victoriano
-- BRIEF: Try to stablish core business rules related to billing. This is a partial fix.


-- Remove null constraint--this is needed by buy_order_processing.add_order() procedure.
alter table buy_orders 
modify column payment_id smallint unsigned;

-- Ensure each product is only associated with one buy order
alter table buy_order_details
add unique(product_id, buy_order_id);

-- Create comment table
create table comment(
	id smallint unsigned primary key auto_increment,
	content varchar(255),
	user_id smallint unsigned not null,
	created_at timestamp not null default now(),
	updated_at timestamp not null default now() on update now(),
	foreign key (user_id) references users(id)
);


-- Create table to map comments to orders
create table order_comment(
	id smallint unsigned primary key auto_increment,
	order_id smallint unsigned not null,
	comment_id smallint unsigned not null unique,
	created_at timestamp not null default now(),
	foreign key (order_id) references orders(id),
	foreign key (comment_id) references comment(id)
);


-- Add comment column to orders table.
alter table orders
add column last_comment_id smallint unsigned;


-- Create order_queue_status table. To be used by order_queue table.
create table order_queue_status(
	id smallint unsigned primary key auto_increment,
	name varchar(25) unique,
	description varchar(255)
);


-- Populate order_queue_status table
INSERT INTO order_queue_status (name, description) VALUES
('Sin asignar', 'La orden está pendiente y aún no se ha asignado'),
('Asignada', 'La orden ya hasido asginada, y está siendo procesada actualmente'),
('Completado', 'La orden ha sido completada y está lista'),
('Cancelado', 'La orden ha sido cancelada'),
('Devuelto', 'La orden ha sido devuelta por el cliente'),
('Reembolsado', 'El importe de la orden ha sido reembolsado al cliente');


-- Rename to a more descriptive name.
rename table taken_order to order_queue;

-- Add new columns: customer_id and order_queue_status_id columns. And corresponding foreign key.
alter table order_queue
add column customer_id smallint unsigned,
add column order_queue_status_id smallint unsigned not null default 1,
add foreign key (customer_id) references customers(id),
add foreign key (order_queue_status_id) references order_queue_status(id);


-- Populate customer_id column from order_queue
update order_queue oq, orders o
set oq.customer_id = o.customer_id
where o.id = oq.order_id;


-- Add NOT NULL constraint to order_queue.customer_id
alter table order_queue 
modify column customer_id smallint unsigned not null;


-- Accept NULL values in salesperson_id column.
alter table order_queue
modify column salesperson_id smallint unsigned;

-- select order_id, is_done, name from order_queue oq join order_queue_status oqs on oqs.id = oq.order_queue_status_id where is_done = true;
-- Assign right status id for completed orders in queue.
update order_queue 
set order_queue_status_id = 3
where is_done = true;


-- Drop is_done column in favor of order_queue_status_id column
alter table order_queue 
drop column is_done;


-- Add price_id column to buy_order_details
alter table buy_order_details
add column price_id smallint unsigned,
add constraint fk_bod_price_id foreign key (price_id) references price_history(id);

-- Populate buy_order_details.price_id column
-- IMPORTANT: This should be one of the first operation when passing to production.
update buy_order_details bod
set price_id = (select id from price_history 
                where price_type = 'buy' 
                    and thru_date is null 
                    and product_id = bod.product_id)
where price_id is null;

-- Set null constraint to buy_order_details.price_id column
alter table buy_order_details
modify column price_id smallint unsigned not null;


-- Check everything is looking fine.
select c.id as customer_id, s.id as salesperson_id , o.id as order_id
from orders o
join customers c on o.customer_id = c.id
join salesperson s on c.salesperson_id = s.id 
where s.user_id =  (select id from users where username = 'josevictoriano');

select c.id as customer_id, s.id as salesperson_id , o.id as order_id
from orders o
join customers c on o.customer_id = c.id
left join salesperson s on c.salesperson_id = s.id 
where s.user_id !=  (select id from users where username = 'josevictoriano');

select * from person p join customers c on c.person_id = p.id where c.id in (98, 99, 100);

-- +-+-+-+-+-+-++-+-+-+-+-+-+
--          Triggers
-- +-+-+-+-+-+-++-+-+-+-+-+-+

/**
 * Triggered on new insert in `order_comment table`.
 * Will update the order's last comment for the corresponding last inserted comment.
 */
create trigger tr_order_comment_after_insert
after insert on order_comment for each row
    update orders set last_comment_id = new.id
    where id = new.order_id;


-- +-+-+-+-+-+-++-+-+-+-+-+-+
--      Stored Procedures
-- +-+-+-+-+-+-++-+-+-+-+-+-+
set sql_mode=oracle;

create or replace package order_api as
    -- Update the order's latest_comment_id to each order having last_comment_id as null.
    procedure update_last_comment_id();
end;

create or replace package body order_api as
    procedure update_last_comment_id() as
    begin
        update orders o
        set last_comment_id = (select id
                               from order_comment oc
                               where o.id = oc.order_id
                               order by oc.created_at desc
                               limit 1)
        where last_comment_id is null;
    end;
end order_api;
set sql_mode=oracle;

select o.id as order_id, payment_id, customer_id, oc.id as comment_id, oc.created_at
from orders o
join order_comment oc on o.id = oc.order_id
-- group by o.id
order by oc.created_at desc;

select id, last_comment_id from orders;

call order_api.update_last_comment_id();

select * from order_comment oc where oc.order_id = 383;
