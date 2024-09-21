resource "aws_iam_role" "glue_role" {
  name               = "Cloud9-${var.project}-glue-role"
  assume_role_policy = data.aws_iam_policy_document.glue_base_policy.json
}

resource "aws_iam_role_policy" "task_role_policy" {
  name   = "${var.project}-glue-role-policy"
  role   = aws_iam_role.glue_role.id
  policy = data.aws_iam_policy_document.glue_access_policy.json
}
