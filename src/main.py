import requests
import boto3

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

def fetch_api():
    try:
        response = requests.get(API_URL)
        response.raise_for_status

        return response.json()

    except Exception as e:
        print(f'Erro na requisição da API {e}')


def main():
    create_s3_bucket()
    create_glue_database()

    fetch_api()

main()