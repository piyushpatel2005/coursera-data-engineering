data "archive_file" "transformation_lambda" {
  type        = "zip"
  source_file = "${path.root}/assets/transformation_lambda/main.py"
  output_path = "${path.root}/assets/transformation_lambda/lambda.zip"
}

resource "aws_lambda_function" "transformation_lambda" {
  function_name = "${var.project}-transformation-lambda"
  description   = "Lambda function to transform data in Kinesis Firehose"
  architectures = ["arm64"]
  runtime       = "python3.12"
  handler       = "main.lambda_handler"
  role          = aws_iam_role.transformation_lambda_role.arn

  package_type = "Zip"
  filename     = data.archive_file.transformation_lambda.output_path

  memory_size = 128
  ephemeral_storage {
    size = 512
  }
  timeout = 60
  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      URL_LAMBDA_INFERENCE = var.inference_api_url
    }
  }

  source_code_hash = data.archive_file.transformation_lambda.output_sha
}
