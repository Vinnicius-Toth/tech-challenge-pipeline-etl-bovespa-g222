resource "aws_glue_job" "glue_job_etl_details" {
  name     = var.glue_job_name_details
  role_arn = "arn:aws:iam::569358226624:role/LabRole"

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_artifact_name}/glue_details/app/src/main.py"
    python_version  = "3"
  }

  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"                 

  default_arguments = {
    "--enable-metrics"    = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--job-language"      = "python"
    "--job-bookmark-option" = "job-bookmark-disable"
    "--job_name"            = var.glue_job_name_details
    "--bucket_ingestion"  = var.bucket_ingestao_etl_name
    "--bucket_results_athena"  = var.bucket_results_athena_name
    "--database_name"  = "db_ibovespa_data"
    "--table_name"  = "tb_cotacao_ibovespa"
  }
  execution_class = "STANDARD" 
}