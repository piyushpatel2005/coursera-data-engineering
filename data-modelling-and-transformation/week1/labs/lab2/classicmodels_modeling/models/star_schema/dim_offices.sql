SELECT 
    {{ dbt_utils.generate_surrogate_key(['officeCode']) }} as office_key, 
    postalCode as postal_code, 
    city as city, 
    state as state, 
    country as country, 
    territory as territory
FROM {{var("source_schema")}}.offices