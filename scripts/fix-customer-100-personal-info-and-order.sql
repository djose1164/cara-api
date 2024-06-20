-- Arregla el nombre del ciente.
-- Arregla orden factura a cliente incorrecto


update contacts 
set forename = 'Agustina'
where id = 109;


update orders 
set customer_id = 100
where id = 393;



