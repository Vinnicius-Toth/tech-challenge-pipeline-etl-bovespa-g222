# Buckets S3
variable "bucket_ingestao_etl_name" {
  description = "The name of the S3 bucket for ETL ingestion"
  type        = string
  default     = "bucket-techchallenge-ingestao-bovespa-g222"
}

variable "bucket_artifact_name" {
  description = "The name of the S3 bucket for ETL ingestion"
  type        = string
  default     = "bucket-techchallenge-artifacts-g222"
}

variable "bucket_results_athena_name" {
  description = "The name of the S3 bucket for ETL ingestion"
  type        = string
  default     = "bucket-techchallenge-results_athena-g222"
}

variable "bucket_states_terraform_name" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "bucket-techchallenge-states-terraform-g222"
}

variable "glue_job_name" {
  description = "The name of glue job"
  type        = string
  default     = "glue_job_etl_ingestion_refined"
}

# Configuracoes gerais
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