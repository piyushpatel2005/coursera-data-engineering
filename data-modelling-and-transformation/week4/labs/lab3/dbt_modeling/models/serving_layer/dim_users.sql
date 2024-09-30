SELECT
user_id,
user_lastname,
user_name,
user_since,
place_name,
country_code
from {{var("source_schema")}}.users