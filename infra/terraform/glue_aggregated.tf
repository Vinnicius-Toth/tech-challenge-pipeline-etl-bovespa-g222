resource "aws_glue_job" "glue_job_etl_aggregated" {
  name     = var.glue_job_name_aggregated
  role_arn = "arn:aws:iam::569358226624:role/LabRole"

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_artifact_name}/glue_aggregated/app/src/main.py"
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
    "--job_name"            = var.glue_job_name_aggregated
    "--bucket_results_athena"  = var.bucket_results_athena_name
    "--database_name"  = "db_ibovespa_data"
    "--table_name_read"  = "tb_cotacao_ibovespa"
    "--table_name_write"  = "tb_cotacao_ibovespa_aggregated"
  }
  execution_class = "STANDARD" 
}