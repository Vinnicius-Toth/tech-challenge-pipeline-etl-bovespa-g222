resource "aws_lambda_function" "process_s3_event" {
  function_name = "lambda-trigger-glue-job"
  role          = "arn:aws:iam::569358226624:role/LabRole"
  handler       = "index.handler"
  runtime       = "python3.9"
  timeout       = 10

  s3_bucket         = var.bucket_artifact_name
  s3_key            = "lambdas/process_s3_event.zip"
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_s3_event.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket_ingestao_etl.arn
}

resource "aws_s3_bucket_notification" "s3_event_trigger" {
  bucket = aws_s3_bucket.bucket_ingestao_etl.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_s3_event.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
