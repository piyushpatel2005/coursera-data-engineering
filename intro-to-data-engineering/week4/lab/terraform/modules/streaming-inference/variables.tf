variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "kinesis_stream_arn" {
  type        = string
  description = "Source Kinesis data stream arn"
}

variable "inference_api_url" {
  type        = string
  description = "URL of the API to use for inference"
}
