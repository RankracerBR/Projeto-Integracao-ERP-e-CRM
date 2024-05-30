import boto3
import json

s3_client = boto3.client("s3")
S3_BUCKET = 'test-lambda-api-project'

def lambda_handler(event, context):
    object_key = "modified_data.json"  # replace object key
    try:
        file_content = s3_client.get_object(Bucket=S3_BUCKET, Key=object_key)["Body"].read().decode('utf-8')
        print(file_content)
        return {
            'statusCode': 200,
            'body': file_content
        }
    except Exception as e:
        print(f"Error reading data from S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
