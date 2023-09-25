drop table PRODUCT_CATEGORY;
CREATE TABLE product_category(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(32) UNIQUE NOT NULL,
	description VARCHAR(128)
);

INSERT INTO product_category(name)
VALUES('Desinfetante'), ('Ambientadores'), ('Lavanderia');

INSERT INTO product_category(name)
VALUES('Jabones');

ALTER TABLE products
ADD COLUMN category_id SMALLINT UNSIGNED DEFAULT 1,
ADD FOREIGN KEY (category_id) REFERENCES product_category(id);

UPDATE products 
SET name = 'Ambientador Chicle'
WHERE name = 'Ambietador Chicle';

UPDATE products
SET category_id = 2
WHERE name LIKE 'Ambientador%';

UPDATE products
SET category_id = 4
WHERE name LIKE 'Jabon%' OR name = 'Lavaplatos';

UPDATE products 
SET category_id = 3
WHERE name = 'Suavitel';
