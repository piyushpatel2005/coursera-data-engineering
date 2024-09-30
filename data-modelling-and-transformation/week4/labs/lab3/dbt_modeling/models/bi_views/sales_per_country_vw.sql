SELECT
date_part('month', fs.session_start_time) AS session_month,
date_part('year', fs.session_start_time) AS session_year,
du.country_code,
SUM(fs.price) AS total_sales
FROM {{var("target_schema")}}.fact_session fs
LEFT JOIN {{var("target_schema")}}.dim_users du
ON fs.user_id = du.user_id
GROUP BY 1,2,3