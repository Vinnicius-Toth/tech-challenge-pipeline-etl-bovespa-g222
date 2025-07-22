output "bucket_ingestao_etl_name" {
  value = aws_s3_bucket.bucket_ingestao_etl.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.bucket_ingestao_etl.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.process_s3_event.function_name
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_exec_role.arn
}