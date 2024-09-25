# Dashboard
resource "aws_cloudwatch_dashboard" "rds_dashboard" {
  dashboard_name = "${var.project}-rds-dashboard"

  dashboard_body = jsonencode({
    widgets = [

      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1

        properties = {
          markdown = "RDS Dashboard for ${var.rds_instance_id}"
        }
      },

      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            [
              "AWS/RDS",
              "CPUUtilization",
              "DBInstanceIdentifier",
              "${var.rds_instance_id}"
            ]
          ]
          period = 30
          stat   = "Average"
          region = "us-east-1"
          title  = "${var.rds_instance_id} - CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 7
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "${var.rds_instance_id}"]
          ]
          period = 30
          stat   = "Average"
          region = "us-east-1"
          title  = "${var.rds_instance_id} - Free Storage Space"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 13
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.rds_instance_id}"]
          ]
          period = 30
          stat   = "Average"
          region = "us-east-1"
          title  = "${var.rds_instance_id} - Database Connections"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 13
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", "${var.rds_instance_id}"],
            ["AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", "${var.rds_instance_id}"]
          ]
          period = 30
          stat   = "Average"
          region = "us-east-1"
          title  = "${var.rds_instance_id} - Read/Write IOPS"
        }
      }

    ]
  })
}


# Alerts
resource "aws_cloudwatch_metric_alarm" "BastionStatus" {
  alarm_name          = "${var.project}-bastion-status"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "StatusCheckFailed_Instance"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "0"
  alarm_description   = "This metric monitors Bastion status"
  alarm_actions       = [aws_sns_topic.cloudwatch_updates.arn]
  dimensions = {
    InstanceId = var.bastion_host_id
  }
}

resource "aws_sns_topic" "cloudwatch_updates" {
  name = "${var.project}-cloudwatch-notifications"
}


resource "aws_sns_topic_subscription" "cloudwatch_email_sub" {
  topic_arn = aws_sns_topic.cloudwatch_updates.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# RDS Alert
### START CODE HERE ### (~ 15 lines of code)
resource "aws_cloudwatch_metric_alarm" "RdsCpuUsage" {
  alarm_name          = "${var.project}-rds-status"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2" # Set the number of evaluation periods to 2
  metric_name         = "CPUUtilization" # Use the "CPUUtilization" metric
  namespace           = "AWS/RDS"
  period              = "60" # Set the period to "60"
  statistic           = "Maximum"
  threshold           = "20" # Set the threshold to 20. This is 20% of CPU utilization
  alarm_description   = "This metric monitors RDS CPU Utilization"
  alarm_actions       = [aws_sns_topic.cloudwatch_updates.arn] # Get the arn of the sns topic cloudwatch_updates
  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }
}
### END CODE HERE ###