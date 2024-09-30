resource "aws_glue_data_quality_ruleset" "songs_dq_ruleset" {
  name    = "songs_dq_ruleset"
  ruleset = "Rules = [ IsComplete \"track_id\", ColumnLength \"track_id\" = 18, IsComplete \"song_id\", ColumnLength \"song_id\" = 18, IsComplete \"artist_id\"]"
  target_table {
    database_name = var.catalog_database
    table_name    = "songs"
  }
}

resource "aws_glue_data_quality_ruleset" "sessions_dq_ruleset" {
  name    = "sessions_dq_ruleset"
  ruleset = "Rules = [ IsComplete \"user_id\", IsComplete \"session_id\", ColumnLength \"user_id\" = 36, ColumnLength \"session_id\" = 36, IsComplete \"song_id\", ColumnValues \"price\" <= 2 ]"
  target_table {
    database_name = var.catalog_database
    table_name    = "sessions"
  }
}

resource "aws_glue_data_quality_ruleset" "users_dq_ruleset" {
  name    = "users_dq_ruleset"
  ruleset = "Rules = [ IsComplete \"user_id\", Uniqueness \"user_id\" > 0.95, IsComplete \"user_lastname\", IsComplete \"user_name\", IsComplete \"user_since\" ]"
  target_table {
    database_name = var.catalog_database
    table_name    = "users"
  }
}