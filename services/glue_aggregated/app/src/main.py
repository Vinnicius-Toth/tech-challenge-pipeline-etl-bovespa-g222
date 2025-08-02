import sys
import re
import unicodedata
import boto3
import time
import logging
import pytz
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import col, lit
from pyspark.sql.types import StringType, IntegerType, DoubleType, BooleanType, DateType, TimestampType
from pyspark.sql.functions import regexp_replace, col, trim
from datetime import datetime

# Log config
class Logs:
    def __init__(self, name="glue_job"):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)
        raise Exception(msg)

## Extract 

def read_table_from_catalog(glueContext, database_name, table_name, anomesdia):
    """
    Read table from Glue Catalog
    """
    log.info(f"Reading table in Glue Catalog: {database_name}.{table_name}")
    try:
        dyf = glueContext.create_dynamic_frame.from_catalog(
            database=database_name,
            table_name=table_name,
            push_down_predicate=anomesdia
        )
        log.info("Read table in Glue Catalog was a sucessefuly!")
        
        df = dyf.toDF()
        return df
    
    except Exception as e:
        log.error(f"Error while read table in Glue Catalog: {e}")

## Transform
def execute_aggregate_transformation(spark, df):
    log.info("Executing transformation SQL in Dataframe")
    try:        
        df.createOrReplaceTempView("view_df_ibovespa")

        result_df = spark.sql(""" 
            select 
                sum(qtde_teorica) as sum_qtde_teorica
                ,ingestion_type   as ingestion_type
                ,anomesdia        as anomesdia
            from view_df_ibovespa 
            group by ingestion_type, anomesdia
            order by anomesdia
        """)

        log.info("Transformation with SQL was a sucessfuly!")
        return result_df
    except Exception as e:
        log.error(f"Error while executing transformation with SQL: {e}")


def convert_df_to_dyf(df, glueContext):
    log.info("Converting dataframe to DynamicFrame")

    try:
        return DynamicFrame.fromDF(df, glueContext, "dyf")
    
    except Exception as e:
        log.error(f"Error while converting dataframe to DynamicFrame - {e}")


## Load
def load_ingestion_in_glue_table(glueContext, dyf, database_name, table_name):
    """ 
    Upload csv file to democratize data in Gluetable

    """
    log.info(f"Uploading data on glue data catalog table - {database_name}.{table_name}")
    
    try:
        glueContext.write_dynamic_frame.from_catalog(
                frame=dyf,
                database=database_name,
                table_name=table_name,
                additional_options={"partitionKeys": ["anomesdia"]},
                transformation_ctx="datasink",
                writeDisposition="overwrite"
            )
            
    except Exception as e:
        log.error(f"Error while uploading data on glue data catalog table - {e}")

    log.info(f"Data upload was sucessefuly!")

def run_msck_repair(database, table, output_location):
    try:
        log.info(f"Running MSCK Repair in table - {database}.{table}")
        athena = boto3.client('athena')
        query = f"MSCK REPAIR TABLE {table}"
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        query_execution_id = response['QueryExecutionId']
        # Aguarda a execução terminar (opcional)
        while True:
            result = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = result['QueryExecution']['Status']['State']
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                log.info(f"Athena query state: {state}")
                break
            time.sleep(2)

    except Exception as e:
        log.error(f"Error while run msk repair in Athena: {e}")

## Utils
def create_session(job_name):
    """
    Create session and instantiate gluejob
    return: spark, glueContext
    """
    log.info(f"Start session in job - {job_name}")

    try:
        sc = SparkContext()
        glueContext = GlueContext(sc)
        spark = glueContext.spark_session
    
    except Exception as e:
        log.error(f"Failed while create session - {e}")

    log.info("Session start with sucesseful")
    return spark, glueContext


def main():
    global log 
    log = Logs()
    
    # Get parameters
    parameters = [
        'JOB_NAME',
        'bucket_ingestion',
        'bucket_results_athena',
        'database_name',
        'table_name_read',
        'table_name_write',
        'anomesdia'
    ]
    args = getResolvedOptions(sys.argv, parameters)
    
    job_name = args['JOB_NAME']
    bucket_ingestion = args['bucket_ingestion']
    bucket_results_athena = args['bucket_results_athena']
    database_name = args['database_name']
    table_name_read = args['table_name_read']
    table_name_write = args['table_name_write']
    anomesdia = int(args['anomesdia'])

    # Start Ingestion
    spark, glueContext = create_session(job_name)

    # Extract
    df = read_table_from_catalog(glueContext, database_name, table_name_read, anomesdia)
    
    # Transform
    df = execute_aggregate_transformation(spark, df)

    dyf = convert_df_to_dyf(df, glueContext)

    # Load
    load_ingestion_in_glue_table(glueContext, dyf, database_name, table_name_write)

    run_msck_repair(
        database=database_name,
        table=table_name_write,
        output_location=f's3://{bucket_results_athena}/'
    )


if __name__ == '__main__':
    main()