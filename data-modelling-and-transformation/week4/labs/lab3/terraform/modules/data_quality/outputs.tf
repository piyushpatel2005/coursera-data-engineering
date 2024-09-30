output "songs_db_ruleset" {
  value = aws_glue_data_quality_ruleset.songs_dq_ruleset.name
}

output "sessions_db_ruleset" {
  value = aws_glue_data_quality_ruleset.sessions_dq_ruleset.name
}

output "users_db_ruleset" {
  value = aws_glue_data_quality_ruleset.users_dq_ruleset.name
}