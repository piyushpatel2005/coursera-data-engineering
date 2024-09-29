SELECT
    {{ dbt_utils.generate_surrogate_key(['employeeNumber']) }} as employee_key,
    lastName as employee_last_name, 
    firstName as employee_first_name, 
    jobTitle as job_title, 
    email as email
FROM {{var("source_schema")}}.employees