SELECT DISTINCT
artist_id,
artist_mbid,
artist_name
from {{var("source_schema")}}.songs