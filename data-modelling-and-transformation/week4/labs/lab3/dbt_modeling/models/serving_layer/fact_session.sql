SELECT
session_id,
user_id,
song_id,
artist_id,
price,
liked,
liked_since,
session_start_time
from {{var("source_schema")}}.sessions