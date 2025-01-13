import requests

API_URL = 'https://restcountries.com/v3.1/lang/portuguese'

def fetch_api():
    try:
        response = requests.get(API_URL)
        response.raise_for_status

        return response.json()

    except Exception as e:
        print(f'Erro na requisição da API {e}')


def main():
    fetch_api()

main()