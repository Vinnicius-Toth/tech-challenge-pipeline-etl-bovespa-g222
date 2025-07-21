resource "aws_s3_bucket" "bucket-ingestao-etl" {
  bucket = var.bucket_ingestao_etl_name
  acl    = var.acl

  versioning {
    enabled = true
  }

  tags = {
    Name        = var.bucket_ingestao_etl_name
    Environment = var.environment
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