CREATE VIEW product_statistics
AS
SELECT SUM(quantity) AS quantity, name, product_id, image_url
FROM products p
JOIN order_details od ON od.product_id  = p.id
GROUP BY product_id
ORDER BY 1 DESC;
	
ALTER DEFINER='cara-api'@'%' VIEW bill_statistics 
AS 
select concat(`pi2`.`forename`,' ',`pi2`.`surname`) AS `name`,`pi2`.`customer_id` AS `customer_id`,count(`ps`.`status`) AS `bill_quantity`,`ps`.`status` AS `status`,sum(`p`.`paid_amount`) AS `paid_amount`,sum(`p`.`amount_to_pay`) AS `amount_to_pay` 
from (((`cara_testing`.`person_info` `pi2` 
join `cara_testing`.`orders` `o` on(`o`.`customer_id` = `pi2`.`customer_id`)) 
join `cara_testing`.`payments` `p` on(`p`.`id` = `o`.`payment_id`))
join `cara_testing`.`payment_status` `ps` on(`ps`.`id` = `p`.`payment_status_id`)) 
group by `ps`.`status`,`pi2`.`customer_id` 
order by `ps`.`status`,count(`ps`.`status`) desc,concat(`pi2`.`forename`,' ',`pi2`.`surname`);
