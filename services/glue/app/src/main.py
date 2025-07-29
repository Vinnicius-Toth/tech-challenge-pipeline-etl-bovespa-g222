import sys
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col


## Extract
def read_csv_files(spark, path_s3):
    df = spark.read.\
        option("header", "true").\
        option("inferSchema", "true").\
        csv(path_s3)
    
    return df


## Transform

## Load

##Utils
def create_session():
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session


    return spark, glueContext

def main():
    print('inicio')
    parameters = [
        'JOB_NAME',
        'bucket_ingestion' 
    ]
    args = getResolvedOptions(sys.argv, parameters)
    
    # Parameters
    print('Parameters')
    job_name = args['JOB_NAME']
    bucket_ingestion = args['bucket_ingestion']

    # Start
    print('sessao')
    spark, glueContext = create_session()
    # Extract 
    print('leitura')
    df = read_csv_files(spark, bucket_ingestion)
    df.show()

    # Transform

    # Load

    # End


     
if __name__ == '__main__':
    main()


