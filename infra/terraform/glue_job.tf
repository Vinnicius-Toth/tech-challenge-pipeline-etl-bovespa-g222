resource "aws_glue_job" "glue_job_etl" {
  name     = var.glue_job_name
  role_arn = "arn:aws:iam::569358226624:role/LabRole"

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_artifact_name}/glue/app/src/main.py"
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
    "--job_name"            = var.glue_job_name
    "--bucket_ingestion"  = "s3://${var.bucket_ingestao_etl_name}"
    "--database_name"  = "db_ibovespa_data"
    "--table_name"  = "tb_cotacao_ibovesta"
  }
  execution_class = "STANDARD" 
}