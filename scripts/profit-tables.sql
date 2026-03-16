-- CARA API V0.19.0
-- PROFIT TABLES


create table sale(
	id smallint unsigned primary key auto_increment,
	order_id smallint unsigned,
	customer_id smallint unsigned not null,
	total_amount decimal(10, 2) check (total_amount > 0),
	created_at timestamp not null default now(),
	foreign key (customer_id) references customers(id),
	foreign key (order_id) references orders(id)
);


create table sale_item(
	id smallint unsigned primary key auto_increment,
	sale_id smallint unsigned not null,
	product_id smallint unsigned not null,
	quantity smallint unsigned not null,
	unit_price decimal(6, 2) unsigned not null,
	foreign key (sale_id) references sale(id),
	foreign key (product_id) references products(id),
	check(quantity > 0 and unit_price > 0),
	unique(product_id, sale_id),
	index(sale_id)
);

create table commission(
	id smallint unsigned primary key auto_increment,
	rate decimal(4, 2) not null,
	amount decimal(6, 2) check(amount > 0),
	payment_date datetime,
	admin_id smallint unsigned not null,
	salesperson_id smallint unsigned not null,
	created_at timestamp not null default now(),
	foreign key (admin_id) references users(id),
	foreign key (salesperson_id) references salesperson(id),
	constraint chk_rate check(rate > 0 and rate <= 1),
	index(salesperson_id)
);


create table commission_item(
    id smallint unsigned primary key auto_increment,
    commission_id smallint unsigned not null,
    product_id smallint unsigned not null,
    quantity smallint unsigned not null,
    unit_commission decimal(6, 2) unsigned not null,
    supplier_id smallint unsigned not null,
    foreign key (commission_id) references commission(id)
        on delete cascade,
    foreign key (product_id) references products(id),
    foreign key (supplier_id) references providers(id),
    check(quantity > 0 and unit_commission > 0),
    unique(product_id, commission_id),
    index(commission_id)
);


-- create table salesperson_commission_history(
-- 	id smallint unsigned primary key auto_increment,
-- 	amount decimal(6, 2) not null check(amount > 0),
-- 	product_id smallint unsigned not null,
-- 	created_at timestamp not null default now(),
-- 	foreign key (product_id) references products(id)
-- );

-- create trigger tr_commission_update
-- after update
-- 	on commission
-- for each row
-- insert into salesperson_commission_history(commission_id, amount)
-- values(new.id, new.amount);

select *
from supplier_catalog sc;

-- Make combination of product_id and supplier_id unique
alter table supplier_catalog
add constraint uq_supplier_id_product_id unique(supplier_id, product_id);

-- Fix organization's description
update organization 
set short_description = 'La limpieza de tu hogar'
where id = 1;


-- Insert missing products into supplier_catalog.
insert into supplier_catalog(product_id, supplier_id)
select id as product_id, 1 as supplier_id
from products
where id not in (select product_id from supplier_catalog);
