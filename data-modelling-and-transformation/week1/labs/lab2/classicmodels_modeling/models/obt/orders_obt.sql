SELECT
    orderdetails.orderNumber as order_number,
    orderdetails.orderLineNumber as order_line_number,
    products.productName as product_name,
    products.productScale as product_scale,
    products.productVendor as product_vendor,
    products.productDescription as product_description,
    products.buyPrice as product_buy_price,
    products.MSRP as product_msrp,
    productlines.textDescription as product_line,
    orderdetails.quantityOrdered as quantity_ordered,
    orderdetails.priceEach as product_price,
    orders.orderDate as order_date,
    orders.requiredDate as order_required_date,
    orders.shippedDate as order_shipped_date,
    customers.customerName as customer_name,
    customers.city as customer_city,
    customers.state as customer_state,
    customers.postalCode as customer_postal_code,
    customers.creditLimit as customer_credit_limit,
    employees.firstName as sales_rep_first_name,
    employees.lastName as sales_rep_last_name,
    employees.jobTitle as sales_rep_title,
    orders.status as order_status,
    orders.comments as order_comments
FROM {{var("source_schema")}}.orderdetails
JOIN {{var("source_schema")}}.orders ON orderdetails.orderNumber =  orders.orderNumber
JOIN {{var("source_schema")}}.products ON orderdetails.productCode =  products.productCode
JOIN {{var("source_schema")}}.productlines ON products.productLine =  productlines.productLine
JOIN {{var("source_schema")}}.customers ON orders.customerNumber =  customers.customerNumber
JOIN {{var("source_schema")}}.employees ON customers.salesRepEmployeeNumber =  employees.employeeNumber