SELECT 
    {{ dbt_utils.generate_surrogate_key(['customerNumber']) }} as customer_key, 
    customerName as customer_name,   
    contactLastName as customer_last_name, 
    contactFirstName as customer_first_name, 
    phone as phone, 
    addressLine1 as address_line_1, 
    addressLine2 as address_line_2, 
    postalCode as postal_code, 
    city as city, 
    state as state, 
    country as country,
    creditLimit as credit_limit
FROM {{var("source_schema")}}.customers