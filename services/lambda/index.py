import json

def handler(event, context):
    for record in event.get('Records', []):
        s3_info = record['s3']
        bucket_name = s3_info['bucket']['name']
        object_key = s3_info['object']['key']
        
        print(f"Novo arquivo recebido no bucket {bucket_name}: {object_key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Evento processado com sucesso!')
    }