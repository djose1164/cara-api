-- CARA API - 0.19.0
-- BRIEF: We want to keep an history of price change; when we update a price the invoce's total shouldn't change.


-- create table price_history(
-- 	id smallint unsigned primary key auto_increment,
-- 	price decimal(10, 2),
-- 	start_date datetime not null default now(),
-- 	thru_date datetime,
-- 	product_id smallint unsigned not null,
-- 	foreign key (product_id) references products(id),
-- 	index (start_date, thru_date),
-- 	constraint chk_dates check (thru_date is null or start_date < thru_date)
-- );

create table price_history_bk as select * from price_history;

insert into price_history(price, start_date, thru_date, product_id, price_type)
select price, start_date, thru_date, product_id, 'sell' as price_type 
from price_history_bk;

create table price_history(
	id smallint unsigned primary key auto_increment,
	price decimal(10, 2),
	start_date datetime not null default now(),
	thru_date datetime,
	product_id smallint unsigned not null,
	supplier_id smallint unsigned,
	price_type enum('buy', 'sell') not null, 
	foreign key (supplier_id) references providers(id),
	foreign key (product_id) references products(id),
	index (start_date, thru_date),
	index (product_id),
	constraint chk_dates check (thru_date is null or start_date < thru_date),
	constraint chk_price_type check(price_type = 'sell' or (price_type = 'buy' and supplier_id is not null)),
	constraint chk_price check(price > 0)
);

-- Only if the table already exists, it's needed to alter it.
alter table price_history
add constraint chk_price check(price > 0);

-- Populate buy prices from price_history table
insert into price_history(price, product_id, price_type, supplier_id)
select buy_price, id, 'buy' as price_type, 1 as supplier_id 
from products;


-- Populate sell prices from price_history table
insert into price_history(price, product_id, price_type)
select sell_price, id, 'sell' as price_type
from products;


-- create table customer_pricing(
-- 	id smallint unsigned primary key auto_increment,
-- 	customer_id smallint unsigned not null,
-- 	product_id smallint unsigned not null,
-- 	price_id smallint unsigned not null,
-- 	created_at timestamp not null default now(),
-- 	foreign key (customer_id) references customers(id),
-- 	foreign key (product_id) references products(id),
-- 	foreign key (price_id) references price_history(id),
-- 	index (customer_id),
-- 	unique (customer_id, product_id, price_id)
-- );

-- Populate customer_pricing; we need to insert a unique combination of customer_, price_ & product_id
-- insert into customer_pricing (customer_id, price_id, product_id)
-- select c.id, ph.id, p.id
-- from customers c, price_history ph, products p
-- where ph.product_id = p.id;
-- select * from customer_pricing;


-- Create supplier_catalog table. This map supplier and their products.
create table supplier_catalog(
	id smallint unsigned primary key auto_increment,
	product_id smallint unsigned not null,
	supplier_id smallint unsigned not null,
	foreign key (supplier_id) references providers(id),
	foreign key (product_id) references products(id),
	index (supplier_id),
	index(product_id)
);


-- Populate supplier_catalog table
insert into supplier_catalog(product_id, supplier_id)
select id, 1 as supplier_id
from products;


-- Add unitary price of product to order_details
alter table order_details 
add column price_id smallint unsigned,-- not null,
add foreign key (price_id) references price_history(id);


select *
from price_history ph 
join supplier_catalog sc on ph.supplier_id = sc.supplier_id and ph.product_id = sc.product_id;


-- Populate price_id column from order_details table
-- (select id from price_history ph2 where ph2.product_id = od.product_id and thru_date is null) to update to current price
update order_details od
    join price_history ph on od.product_id = ph.product_id 
set od.price_id = (select id 
                   from price_history ph2 
                   where ph2.thru_date is null 
                        and ph2.product_id = od.product_id
                        and ph2.price_type = 'sell')
where od.price_id is NULL;


-- Add not null constraint to price_id column.
alter table order_details 
modify column price_id smallint unsigned not null;


-- Create backup for products table
create table products_bk 
    as select * from products;


-- Remove buy_price & sell_price columns from products table.
alter table products
drop column buy_price,
drop column sell_price;



select *
from orders o
into outfile '/exports/hola.csv' 
fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

select p.name, count(*) as total
from price_history ph 
join products p on ph.product_id = p.id
where ph.thru_date is null
group by p.id;

-- Supplier's catalog.
SELECT products.*, price_history.*
FROM products 
JOIN supplier_catalog ON products.id = supplier_catalog.product_id 
JOIN price_history ON products.id = price_history.product_id and price_history.supplier_id = 1
WHERE supplier_catalog.supplier_id = 1 AND price_history.price_type = 'buy' ORDER BY products.category_id;

select *
from buy_orders bys
join buy_order_details bod on bys.id = bod.buy_order_id
join price_history ph on ph.product_id = bod.product_id and ph.supplier_id = bys.provider_id and ph.thru_date is null
where bys.salesperson_id = 1;

