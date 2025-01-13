import requests
import boto3
import json

# AWS
region = 'us-east-1'
bucket_name = 'rest-countries-data-lake'
glue_db_name = 'glue-countries-lake'

# Clients
s3_client = boto3.client('s3', region_name=region)
glue_client = boto3.client('glue', region_name=region)

# Rest Countries URL
API_URL = 'https://restcountries.com/v3.1/lang/portuguese'

def create_s3_bucket():
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f'Bucket {bucket_name} criado com sucesso')
    except Exception as e:
        print(f'Erro ao criar o {bucket_name}: {e}')

def create_glue_database():
    try:
        glue_client.create_database(
            DatabaseInput = {
                'Name': glue_db_name,
                'Description': 'Glue database for Steam analytics'
            }
        )
        print(f'O banco de dados {glue_db_name} do glue foi criado com sucesso')
    except Exception as e:
        print(f'Erro em criar o banco de dados do glue: {e}')

def upload_to_S3(country):
    try:
        country_json = convert_to_json(country)
        filename = 'raw-data/country.json'

        s3_client.put_object(
            Bucket = bucket_name,
            Key = filename,
            Body = country_json
        )

        print(f'O arquivo {filename} foi inserido no bucket do s3')
    
    except Exception as e:
        print(f'Ocorreu um erro {e}')

def fetch_api():
    try:
        response = requests.get(API_URL)
        response.raise_for_status

        return response.json()

    except Exception as e:
        print(f'Erro na requisição da API {e}')

def convert_to_json(data):
    return "\n".join([json.dumps(record) for record in data])

def main():
    create_s3_bucket()
    create_glue_database()

    country = fetch_api()
    upload_to_S3(country)

main()