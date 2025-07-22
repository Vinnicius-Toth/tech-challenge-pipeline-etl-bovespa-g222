# Bucket S3 for ETL Ingestion
resource "aws_s3_bucket" "bucket_ingestao_etl" {
  bucket = var.bucket_ingestao_etl_name
  acl    = var.acl

  versioning {
    enabled = true
  }

# Bucket artifacts for Lambda functions
resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = var.bucket_artifact_name

  versioning {
    enabled = true
  }

}


# Configure the S3 bucket for storing Terraform state files
terraform {
  backend "s3" {
    bucket = "bucket-techchallenge-states-terraform-g222"
    key    = "infra/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}