output "bucket_ingestao_etl_name" {
  value = aws_s3_bucket.bucket_ingestao_etl.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.bucket_ingestao_etl.arn
}
