output "bucket_ingestao_etl_name" {
  description = "Nome do bucket S3 criado"
  value       = aws_s3_bucket.my_bucket.bucket
}

output "bucket_arn" {
  description = "ARN do bucket S3 criado"
  value       = aws_s3_bucket.my_bucket.arn
}