-- Fix cara user.

delete from users where username = 'cara';

insert into contact(email)
value('admin@cara.com');

insert into person(forename, surname, contact_id)
values('Admin', 'Cara', last_insert_id());

-- Only insert if cara user does not exist.
insert into users 
values(1,'cara','$pbkdf2-sha256$29000$iDHmHEMoxRiDEOI8R2hNSQ$Z7k0ZPeNJMKI2wEWjA0Oz7v34LPwrZ0fVAtgEtfC7Lg',1,last_insert_id());
