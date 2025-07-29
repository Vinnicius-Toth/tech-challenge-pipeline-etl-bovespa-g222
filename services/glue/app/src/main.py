import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Lê os argumentos de job
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Inicializa contexto Spark e Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Inicia o job
job.init(args['JOB_NAME'], args)

# Exemplo: leitura de um arquivo CSV do S3
datasource = glueContext.create_dynamic_frame.from_options(
    format_options={"withHeader": True},
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://meu-bucket-exemplo/input/meu-arquivo.csv"],
        "recurse": True
    },
    transformation_ctx="datasource"
)

# Exemplo: transformação opcional (convertendo para DataFrame e exibindo)
df = datasource.toDF()
df.show()

# Exemplo: salvando resultado transformado no S3 em outro path
datasink = glueContext.write_dynamic_frame.from_options(
    frame=datasource,
    connection_type="s3",
    connection_options={"path": "s3://meu-bucket-exemplo/output/"},
    format="csv",
    transformation_ctx="datasink"
)

# Finaliza o job
job.commit()