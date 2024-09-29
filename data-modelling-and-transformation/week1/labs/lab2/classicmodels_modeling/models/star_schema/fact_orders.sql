SELECT 
    {{ dbt_utils.generate_surrogate_key(['orders.orderNumber', 'orderdetails.orderLineNumber']) }} as fact_order_key,
    {{ dbt_utils.generate_surrogate_key(['customers.customerNumber']) }} AS customer_key, 
    {{ dbt_utils.generate_surrogate_key(['employees.employeeNumber']) }} AS employee_key,
    {{ dbt_utils.generate_surrogate_key(['offices.officeCode']) }} AS office_key,
    {{ dbt_utils.generate_surrogate_key(['productCode']) }} AS product_key, 
    orders.orderDate AS order_date,
    orders.requiredDate AS order_required_date, 
    orders.shippedDate AS order_shipped_date,
    orderdetails.quantityOrdered AS quantity_ordered, 
    orderdetails.priceEach AS product_price
FROM {{var("source_schema")}}.orders
JOIN {{var("source_schema")}}.orderdetails ON orders.orderNumber = orderdetails.orderNumber
JOIN {{var("source_schema")}}.customers ON orders.customerNumber = customers.customerNumber
JOIN {{var("source_schema")}}.employees ON customers.salesRepEmployeeNumber = employees.employeeNumber
JOIN {{var("source_schema")}}.offices ON employees.officeCode = offices.officeCode