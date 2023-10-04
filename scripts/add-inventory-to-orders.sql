CREATE TABLE warehouse(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL UNIQUE,
	address_id SMALLINT UNSIGNED,
	FOREIGN KEY (address_id) REFERENCES address(id)
);

INSERT INTO warehouse(name, address_id)
VALUES('Caracol Banana', 64), ('Villa Liberaicon', 65);

ALTER TABLE inventory 
ADD COLUMN quantity_available SMALLINT UNSIGNED NOT NULL DEFAULT 0,
ADD COLUMN minimun_stock_level SMALLINT UNSIGNED NOT NULL DEFAULT 5,
ADD COLUMN maximun_stock_level SMALLINT UNSIGNED NOT NULL DEFAULT 30,
ADD COLUMN reorder_point SMALLINT UNSIGNED NOT NULL DEFAULT 10;

SAVEPOINT before_migrating_stocks;

-- Update `quantity_available` with `stocks` from stock table.
UPDATE inventory i, stocks s
SET quantity_available = in_stock
WHERE s.id = stock_id ;

-- Delete `stock_id` column.
SHOW CREATE TABLE inventory;
ALTER TABLE inventory 
DROP CONSTRAINT fk_inventory_stock_id,
DROP COLUMN stock_id;

-- Add warehouse_id column
ALTER TABLE inventory 
ADD COLUMN warehouse_id SMALLINT UNSIGNED,
ADD FOREIGN KEY (warehouse_id) REFERENCES warehouse(id);

ALTER TABLE order_details
ADD COLUMN warehouse_id SMALLINT UNSIGNED NOT NULL DEFAULT 1,
ADD FOREIGN KEY (warehouse_id) REFERENCES warehouse(id);

-- Set the correct warehouse_id
UPDATE inventory i, warehouse w
SET warehouse_id = 1
WHERE admin_id = 5;

UPDATE inventory i, warehouse w
SET warehouse_id = 2
WHERE admin_id = 6;

