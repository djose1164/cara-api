ALTER TABLE users 
ADD COLUMN warehouse_id SMALLINT UNSIGNED,
ADD FOREIGN KEY (warehouse_id) REFERENCES warehouse(id);

UPDATE users 
SET warehouse_id = 1
WHERE id = 5;

UPDATE users 
SET warehouse_id = 2
WHERE id = 6;

DESC users;

