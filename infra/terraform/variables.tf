variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "bucket-techchallenge-ingestao-etl-bovespa-g222"
}

variable "region" {
  description = "The AWS region where the S3 bucket will be created"
  type        = string
  default     = "us-east-1"
}

variable "acl" {
  description = "The canned ACL to apply to the bucket"
  type        = string
  default     = "private"
}

variable "environment" {
  description = "The environment to created services"
  type        = string
  default     = "prod"
}