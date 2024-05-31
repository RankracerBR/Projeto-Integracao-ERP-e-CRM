import os
import logging
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def replace_null_with_none(data):
    if isinstance(data, dict):
        return {k: replace_null_with_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_null_with_none(item) for item in data]
    elif data is None:
        return "Nenhum"
    else:
        return data

def lambda_handler(event, context):
    logger.info(event)

    bucket_name = os.environ.get("BUCKET_NAME", None)
    try:
        if event and bucket_name:
            s3 = boto3.client("s3")

            path_parameters = event.get("pathParameters", {})
            query_parameters = event.get("queryStringParameters", {})

            user_name = path_parameters.get("username")
            file_name = query_parameters.get("filename")

            if not user_name or not file_name:
                raise ValueError("Missing 'username' or 'filename' in the request parameters")

            if not file_name.endswith('.json'):
                raise ValueError("O arquivo deve ter a extensão .json")

            # Baixar o arquivo JSON do S3
            obj = s3.get_object(Bucket=bucket_name, Key=f"{user_name}/{file_name}")
            data = json.loads(obj['Body'].read())

            # Modificar os dados
            data = replace_null_with_none(data)
            data[-1]['status'] = 'finished'

            # Converter os dados modificados de volta para uma string JSON com formatação
            modified_data = json.dumps(data, indent=4, sort_keys=True)

            # Enviar os dados modificados de volta para o S3
            s3.put_object(Bucket=bucket_name, Key=f"{user_name}/{file_name}", Body=modified_data)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Modified data has been uploaded to S3 bucket."}),
            }
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        return {"statusCode": 500, "body": json.dumps("Error processing the request!")}

    return {"statusCode": 500, "body": json.dumps("Error processing the request!")}
