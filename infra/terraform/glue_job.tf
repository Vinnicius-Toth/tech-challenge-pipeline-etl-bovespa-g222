resource "aws_glue_job" "meu_glue_job" {
  name     = "meu-glue-job"
  role_arn = "arn:aws:iam::569358226624:role/LabRole"

  command {
    name            = "glue_job_etl_ingestion_refined"
    script_location = "s3://${var.bucket_artifact_name}/glue/app/src/main.py"
    python_version  = "3"
  }

  max_retries      = 0
  glue_version     = "4.0"
  number_of_workers = 2
  worker_type      = "G.1X"
  timeout          = 10
}