resource "aws_iam_role" "firehose_role" {
  name               = "Cloud9-${var.project}-firehose-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume_role.json
}


resource "aws_iam_role_policy" "firehose_role_policy" {
  name   = "${var.project}-firehose-role-policy"
  role   = aws_iam_role.firehose_role.id
  policy = data.aws_iam_policy_document.firehose_role_policy.json
}

resource "aws_iam_role" "transformation_lambda_role" {
  name               = "Cloud9-${var.project}-transformation-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_execution_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.transformation_lambda_role.name
}

