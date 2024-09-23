resource "aws_iam_role" "rds_role" {
  name               = "Cloud9-${var.project}-rds-role"
  assume_role_policy = data.aws_iam_policy_document.rds_assume_role.json
}


resource "aws_db_instance_role_association" "rds_role_association" {
  db_instance_identifier = aws_db_instance.master_db.identifier
  feature_name           = "s3Import"
  role_arn               = aws_iam_role.rds_role.arn
}
