import boto3
import json
import urllib.request
import urllib.error
import logging

s3_client = boto3.client("s3")
S3_BUCKET = 'test-lambda-api-project'

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_crm_endpoint(json_data):
    try:
        # Extrai a URL do servidor do JSON
        server_url = json_data.get("servers", [{}])[0].get("url")
        if server_url:
            return server_url
        else:
            logger.error("URL do servidor não encontrada no arquivo JSON.")
            return None
    except Exception as e:
        logger.error(f"Erro ao obter a URL do servidor do arquivo JSON: {e}")
        return None

def send_to_crm(data, endpoint):
    try:
        # Converte os dados em formato JSON
        data_json = json.dumps(data).encode('utf-8')
        
        # Realiza a requisição POST para o CRM
        req = urllib.request.Request(endpoint, data=data_json, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                logger.info("Dados enviados com sucesso para o CRM.")
                return True
            else:
                logger.error(f"Falha ao enviar dados para o CRM. Código de status: {response.getcode()}")
                return False
    except urllib.error.HTTPError as e:
        logger.error(f"Falha ao enviar dados para o CRM. Código de erro: {e.code}")
        return False
    except urllib.error.URLError as e:
        logger.error(f"Erro de URL ao enviar dados para o CRM: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar dados para o CRM: {e}")
        return False

def lambda_handler(event, context):
    object_key = "Augusto/modified_data2.json"  # substitua pelo objeto correto
    try:
        file_content = s3_client.get_object(Bucket=S3_BUCKET, Key=object_key)["Body"].read().decode('utf-8')
        logger.info("Conteúdo do arquivo do S3: %s", file_content)
        
        # Convertendo o conteúdo do arquivo JSON para um dicionário Python
        data = json.loads(file_content)
        
        # Carrega o arquivo JSON do CRM
        with open('crm_swagger.json') as json_file:
            crm_json = json.load(json_file)
        
        # Obtém o endpoint do CRM a partir do arquivo JSON do CRM
        crm_endpoint = get_crm_endpoint(crm_json)
        
        if crm_endpoint:
            # Enviando os dados para o CRM e registrando se foi enviado com sucesso ou não nos logs
            if send_to_crm(data, crm_endpoint):
                return {
                    'statusCode': 200,
                    'body': "Dados enviados com sucesso para o CRM."
                }
            else:
                return {
                    'statusCode': 500,
                    'body': "Falha ao enviar dados para o CRM. Consulte os logs para obter mais informações."
                }
        else:
            return {
                'statusCode': 500,
                'body': "Erro ao obter o endpoint do CRM. Consulte os logs para obter mais informações."
            }
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo do S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
