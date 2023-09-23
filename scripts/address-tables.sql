CREATE TABLE country(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE province(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(40) NOT NULL UNIQUE,
	country_id SMALLINT UNSIGNED NOT NULL,
	FOREIGN KEY (country_id) REFERENCES country(id)
);

CREATE TABLE municipality(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(40) NOT NULL UNIQUE,
	province_id SMALLINT UNSIGNED NOT NULL
);

CREATE TABLE sector(
	id SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(40) NOT NULL UNIQUE,
	municipality_id SMALLINT UNSIGNED NOT NULL
);

INSERT INTO country(name)
VALUES("Republica Dominicana");

INSERT INTO province(name, country_id)
VALUES("Monseñor Nouel", 1);

INSERT INTO municipality(name, province_id)
VALUES('Bonao', 1);

INSERT INTO sector(name, province_id)
VALUES('Caracol Banana', 1), ('Villa Liberacion', 1);

ALTER TABLE address 
ADD COLUMN country_id SMALLINT UNSIGNED,
ADD COLUMN province_id SMALLINT UNSIGNED,
ADD COLUMN municipality_id SMALLINT UNSIGNED,
ADD COLUMN sector_id SMALLINT UNSIGNED,
ADD FOREIGN KEY (country_id) REFERENCES country(id),
ADD FOREIGN KEY (province_id) REFERENCES province(id),
ADD FOREIGN KEY (municipality_id) REFERENCES municipality(id),
ADD FOREIGN KEY (sector_id) REFERENCES sector(id);

UPDATE address 
SET
	country_id = 1,
	province_id = 1,
	municipality_id = 1;
SELECT * FROM address;

-- Delete VARCHAR columns
ALTER TABLE address 
DROP COLUMN country,
DROP COLUMN province,
DROP COLUMN municipality;

