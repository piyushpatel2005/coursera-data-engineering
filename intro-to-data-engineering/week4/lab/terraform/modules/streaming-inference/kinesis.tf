resource "aws_kinesis_firehose_delivery_stream" "extended_s3_stream" {
  name = "${var.project}-delivery-stream"

  kinesis_source_configuration {
    kinesis_stream_arn = var.kinesis_stream_arn
    role_arn           = aws_iam_role.firehose_role.arn
  }

  destination = "extended_s3"
  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.recommendations.arn

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = "${var.project}-delivery-stream-logs"
      log_stream_name = "${var.project}-delivery-stream-logstream"
    }

    processing_configuration {
      enabled = "true"

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${aws_lambda_function.transformation_lambda.arn}:$LATEST"
        }
      }
    }

  }
}
