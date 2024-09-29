with date_dimension as (
    select * from {{ ref('dates') }}
)
SELECT
    date_day,
    day_of_week,
    day_of_month,
    day_of_year,
    week_of_year,
    month_of_year,
    month_name,
    quarter_of_year,
    year_number
FROM
    date_dimension d