import json
import boto3

glue = boto3.client('glue')

glue_job_name = 'glue_job_etl_ingestion_ibovespa_details'

def handler(event, context):
    for record in event.get('Records', []):
        s3_info = record['s3']
        bucket_name = s3_info['bucket']['name']
        object_key = s3_info['object']['key']
        
        print(f"New file received in bucket {bucket_name}: {object_key}")

        response = glue.start_job_run(
            JobName=glue_job_name,
            Arguments={
                '--object_key': object_key  
            }
        )
        print(f"Glue Job starded: {response['JobRunId']}")

    return {
        'statusCode': 200,
        'body': json.dumps('Event processing was successful!')
    }