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
from pyspark.sql.functions import regexp_replace, trim
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
def get_catalog_schema(database, table):
    """
    Capture types from the catalog to convert later

    return: schema    
    """
    log.info(f"Getting columns on glue catalog table - {database}.{table}")

    try:
        glue_client = boto3.client('glue')
        response = glue_client.get_table(DatabaseName=database, Name=table)
        columns = response['Table']['StorageDescriptor']['Columns']
        schema = {}
        for col in columns:
            schema[col['Name']] = col['Type']

    except Exception as e:
        log.error(f"Error while getting columns on glue catalog table - {e}")


    log.info(f"Glue catalog columns successfully captured - {schema}")
    return schema


def read_csv_file(spark, path_s3):
    """
    Read csv files as received via parameter

    return: dataframe
    """
    log.info("Readding file csv in bucket S3")

    try:
        df = spark.read.\
            option("header", "true").\
            option("inferSchema", "true").\
            csv(path_s3)
    
    except Exception as e:
        log.error(f"Error on read csv file - {e}")

    log.info(f"Successfully read csv file - {path_s3}")
    return df


## Transform
def glue_type_to_spark(glue_type):
    """
    Type mapping for conversion in spark

    return: mapping
    """
    mapping = {
        'string': StringType(),
        'int': IntegerType(),
        'bigint': IntegerType(),
        'double': DoubleType(),
        'float': DoubleType(),
        'boolean': BooleanType(),
        'date': DateType(),
        'timestamp': TimestampType()
    }
    return mapping.get(glue_type, StringType())

def cast_columns(df, schema):
    log.info("Casting columns on dataframe")

    try:
        for col_name, glue_type in schema.items():
            if col_name in df.columns:
                spark_type = glue_type_to_spark(glue_type)
                # Cast qtde_teorica
                if col_name == "qtde_teorica":
                    df = df.withColumn(
                        "qtde_teorica",
                        regexp_replace(
                            trim(regexp_replace(col("qtde_teorica"), '"', '')), r'\.', ''
                        ).cast("long")
                    )
                # Cast percentual_participacao                     
                elif col_name == "percentual_participacao":
                    df = df.withColumn(col_name, regexp_replace(col(col_name), ",", ".").cast(spark_type))
                # Cast others columns
                else:
                    df = df.withColumn(col_name, col(col_name).cast(spark_type))

    except Exception as e:
        log.error(f"Error while casting columns on dataframe - {e}")

    log.info(f"Casting columns was sucessefuly - {df.printSchema()}")
    return df

def normalize_column(col_name):
    # Specifical normalize
    substitutions = {
        "Part. (%)": "percentual_participacao",
        "Qtde. Teórica": "qtde_teorica"
    }
    if col_name in substitutions:
        return substitutions[col_name]
    
    # Default normalize
    nfkd = unicodedata.normalize('NFKD', col_name)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    normalized = re.sub(r'[^a-zA-Z0-9_]', '_', only_ascii)
    return normalized.lower()

def normalize_columns(df):
    log.info(f"Normalizing columns on dataframe - Current dataframe: {df.printSchema()}")

    try:
        new_columns = [normalize_column(c) for c in df.columns]
    except Exception as e:
        log.error(f"Error while normalizing columns on dataframe - {e}")

    log.info(f"Dataframe with columns normalized - {df.printSchema()}")
    return df.toDF(*new_columns)

def convert_df_to_dyf(df, glueContext):
    log.info("Converting dataframe to DynamicFrame")

    try:
        return DynamicFrame.fromDF(df, glueContext, "dyf")
    
    except Exception as e:
        log.error(f"Error while converting dataframe to DynamicFrame - {e}")


def add_partition_column_anomesdia(df):
    log.info("Adding partition anomesdia")

    try:
        today_str = get_brasilia_date_str()
        df = df.withColumn("anomesdia", lit(today_str))
    except Exception as e:
        log.error("Error while adding partition anomesdia")

    log.info(f"Partition anomesdia add was sucessfuly - {today_str}")
    return df

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
                additional_options={"partitionKeys": ["anomesdia", "ingestion_type"]},
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

def get_brasilia_date_str():
    tz = pytz.timezone('America/Sao_Paulo')
    today_str = datetime.now(tz).strftime("%Y%m%d")
    return today_str  



def main():
    global log 
    log = Logs()
    
    # Get parameters
    parameters = [
        'JOB_NAME',
        'bucket_ingestion',
        'bucket_results_athena',
        'object_key',
        'database_name',
        'table_name'
    ]
    args = getResolvedOptions(sys.argv, parameters)
    
    job_name = args['JOB_NAME']
    bucket_ingestion = args['bucket_ingestion']
    bucket_results_athena = args['bucket_results_athena']
    object_key = args['object_key']
    database_name = args['database_name']
    table_name = args['table_name']
    s3_path = f"s3://{bucket_ingestion}/{object_key}"

    # Start Ingestion
    spark, glueContext = create_session(job_name)

    # Extract
    df = read_csv_file(spark, s3_path)

    catalog_schema = get_catalog_schema(database_name, table_name)
    
    # Transform
    df = normalize_columns(df)
 
    df = cast_columns(df, catalog_schema)

    df = add_partition_column_anomesdia(df)
    
    dyf = convert_df_to_dyf(df, glueContext)

    # Load
    load_ingestion_in_glue_table(glueContext, dyf, database_name, table_name)

    run_msck_repair(
        database=database_name,
        table=table_name,
        output_location=f's3://{bucket_results_athena}/'
    )


if __name__ == '__main__':
    main()