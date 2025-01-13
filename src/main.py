import requests
import boto3
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

# AWS
region = 'us-east-1'
bucket_name = 'rest-countries-data-lake'
glue_db_name = 'glue-countries-lake'

# Clients
s3_client = boto3.client('s3', region_name=region)
glue_client = boto3.client('glue', region_name=region)
athena_client = boto3.client('athena', region_name=region)

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

def create_glue_crawler(crawler_name, s3_target_path):
    try:
        glue_client.create_crawler(
            Name = 'country-crawler',
            Role = os.getenv('GLUE_CRAWLER_ROLE_ARN'),
            DatabaseName = glue_db_name,
            Targets={'S3Targets': [{'Path': s3_target_path}]}
        )

        print(f'O crawler {crawler_name} criado com sucesso ')
    except Exception as e:
        print(f'Ocorreu um erro: {e}')

def upload_to_S3(country, filename):
    try:
        country_json = convert_to_json(country)

        s3_client.put_object(
            Bucket = bucket_name,
            Key = filename,
            Body = country_json
        )

        print(f'O arquivo {filename} foi inserido no bucket do s3')
    
    except Exception as e:
        print(f'Ocorreu um erro ao subir o arquivo no S3 {e}')

def run_glue_crawler(crawler_name):
    try:
        glue_client.start_crawler(Name = crawler_name)
        print(f'O crawler {crawler_name} começou a rodar')

        while glue_client.get_crawler(Name=crawler_name)['Crawler']['State'] != 'READY':
            time.sleep(5)
        
        print(f'O crawler {crawler_name} terminou de rodar e a tabela foi criada no banco {glue_db_name}')

    except Exception as e:
        print(f'Ocorreu um erro ao rodar o crawler {e}')

def query_athena(folder):
    response = athena_client.start_query_execution(
        QueryString=f'SELECT * FROM "{glue_db_name}"."{folder}" LIMIT 10;',
        QueryExecutionContext={'Database': glue_db_name},
        ResultConfiguration={'OutputLocation': f's3://{bucket_name}'}
    )

    query_execution_id = response['QueryExecutionId']
    print(f'Query {query_execution_id} começou a executar')

    while athena_client.get_query_execution(QueryExecutionId=query_execution_id)['QueryExecution']['Status']['State'] != 'SUCCEEDED':
        time.sleep(5)

    results = athena_client.get_query_results(QueryExecutionId=query_execution_id)

    return results

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
    folder = 'raw-data'       
    filename = 'country.json'
    full_file = folder+filename+'/'

    s3_target_path = f"s3://{bucket_name}/{folder}"

    crawler_name = 'country-crawler'

    create_s3_bucket()
    create_glue_database()

    country = fetch_api()
    upload_to_S3(country, full_file)

    create_glue_crawler(crawler_name, s3_target_path)

    run_glue_crawler(crawler_name)

    result = query_athena(folder)

    print(result)

main()