SELECT 
    {{ dbt_utils.generate_surrogate_key(['productCode']) }} as product_key, 
    productName as product_name, 
    products.productLine as product_line, 
    productScale as product_scale, 
    productVendor as product_vendor,
    productDescription as product_description, 
    textDescription as product_line_description
FROM {{var("source_schema")}}.products
JOIN {{var("source_schema")}}.productlines ON products.productLine=productlines.productLine