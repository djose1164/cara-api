create or replace package commission_api
    procedure calculate_amount(p_commission_id int);
end;

create or replace package body commission_api
    procedure calculate_amount(p_commission_id int)
    begin
        update commission
        set amount = (select round(sum(quantity * unit_commission) * (rate/100), 2)
                      from commission_item ci
                      where ci.commission_id = p_commission_id)
        where id = p_commission_id;
    end;
end;
