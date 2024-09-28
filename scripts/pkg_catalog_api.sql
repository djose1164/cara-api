create or replace package catalog_api
    procedure add_product(p_name varchar(64), p_description varchar(64), p_category_id int);
    procedure delete_product(p_id int);

    procedure add_product_image(p_product_id int, p_image_url tinytext);
    procedure delete_product_image(p_image_id int);
end;


create or replace package body catalog_api
    procedure add_product(p_name varchar(64), p_description varchar(64), p_category_id int)
    begin
        insert into products(name, description, category_id)
        values(p_name, p_description, p_category_id);
    end;

    procedure delete_product(p_id int)
    begin
        delete from products
        where id = p_id;
    end;

    procedure add_product_image(p_product_id int, p_image_url tinytext)
    begin
        insert into product_image(product_id, image_url)
        values(p_product_id, p_image_url);
    end;

    procedure delete_product_image(p_image_id int)
    begin
        delete from product_image
        where id = p_image_id;
    end;
end;

desc product_image ;
