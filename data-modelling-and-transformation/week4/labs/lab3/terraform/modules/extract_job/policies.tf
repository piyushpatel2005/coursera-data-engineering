data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "glue_base_policy" {
  statement {
    sid    = "AllowGlueToAssumeRole"
    effect = "Allow"

    principals {
      identifiers = ["glue.amazonaws.com"]
      type        = "Service"
    }

    actions = ["sts:AssumeRole"]
  }

  statement {
    sid    = "AllowEC2ToAssumeRole"
    effect = "Allow"

    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-ec2-role"]
      type        = "AWS"
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "glue_access_policy" {
  statement {
    sid    = "AllowGlueAccess"
    effect = "Allow"
    actions = [
      "s3:*",
      "glue:*",
      "iam:*",
      "logs:*",
      "cloudwatch:*",
      "sqs:*",
      "ec2:*",
      "rds:*",
      "cloudtrail:*"
    ]
    resources = [
      "*",
    ]
  }
}
