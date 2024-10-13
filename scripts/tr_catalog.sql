create table deleted_products like products;

create trigger tr_products_after_delete
after delete
    on products for each row
insert into deleted_products(id, name, description, category_id)
values(old.id, old.name, old.description, old.category_id);