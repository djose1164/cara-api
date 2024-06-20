-- Cara Api - 0.18.0
-- Brief: Make modifications to table structure


-- Remove plural
rename table contacts to contact;

-- Add 'homephone' column
alter table contact
add column homephone varchar(11);


-- Create common table for customer & user.
create table person(
	id smallint unsigned primary key auto_increment,
	forename varchar(64),
	surname varchar(64),
	birthday date,
	contact_id smallint unsigned not null,
	address_id smallint unsigned,
	foreign key (contact_id) references contact(id)
);


-- Populate 'person' table with appropiate data.
insert into person(forename, surname, contact_id, address_id)
select forename, surname, contact_id, c2.address_id
from customers c
join contact c2 on c2.id = c.contact_id;

insert into person(forename, surname, contact_id, address_id)
select forename, surname, contact_id, c2.address_id
from users u
join contact c2 on c2.id = u.contact_id
where c2.id not in (select contact_id from customers where user_id is not null);


-- Add 'address_id' column to 'providers' table;
alter table providers 
add column address_id smallint unsigned;

update providers p, contact c
set p.address_id = c.address_id
where c.id = p.contact_id;


-- Remove 'address_id' column from 'contact' table.
set foreign_key_checks=0;
alter table contact
drop constraint contact_ibfk_1,
drop column address_id;
set foreign_key_checks=1;


-- Add 'person_id' to 'users' table.
alter table users
add column person_id smallint unsigned unique,
add foreign key (person_id) references person(id);

-- Populate 'person_id' column from 'users' table & don't accept null values.
update users, person 
set person_id = person.id
where person.contact_id = users.contact_id ;


-- Remove 'surname' & 'forename' column from 'contact' table.
alter table contact 
drop column surname, 
drop column forename;

-- Remove 'contact_id' column from 'users' table.
set foreign_key_checks=false;
alter table users
drop constraint users_ibfk_1;

alter table users 
drop column contact_id;
set foreign_key_checks=true;


-- We need to fix cara user by running 'fix-cara-user.sql'
alter table users
modify column person_id smallint unsigned not null unique;

show create table users;


-- Add 'person_id' column & populate it, & drop "contact_id" column from 'customers' table.
alter table customers
add column person_id smallint unsigned,
add foreign key (person_id) references person(id);


-- Set corresponding 'person_id' to each customer.
update customers c, person p
set person_id = p.id
where p.contact_id = c.contact_id ;


-- Remove 'address*' columns from 'customers' table.
alter table customers 
drop column address,
drop column address_id;


-- update customers c, customers_copy cp, person p
-- set c.person_id = p.id
-- where p.contact_id = cp.contact_id and c.id = cp.id;
select * from customers ;


alter table customers
modify column person_id smallint unsigned not null;

set foreign_key_checks=false;
alter table customers
drop constraint customers_ibfk_2,
drop column contact_id;
set foreign_key_checks=true;


-- Add 'created-at' column to 'buy_orders' table.
alter table buy_orders 
add column created_at timestamp;

update buy_orders 
set created_at = `date`
where created_at is NULL ;

alter table buy_orders 
modify column created_at timestamp not null default now();

select id, username from users order by id;

