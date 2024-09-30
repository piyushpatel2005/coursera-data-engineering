SELECT
song_id,
track_id,
title,
release,
year
from {{var("source_schema")}}.songs