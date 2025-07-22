# Configure the S3 bucket for storing Terraform state files
terraform {
  backend "s3" {
    bucket = "bucket-techchallenge-states-terraform-g222"
    key    = "infra/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}