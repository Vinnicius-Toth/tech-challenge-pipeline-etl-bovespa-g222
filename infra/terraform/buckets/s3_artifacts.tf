resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = var.bucket_artifact_name

  versioning {
    enabled = true
  }

  tags = {
    Name        = "bucket-artifacts"
    Environment = var.environment
  }
}