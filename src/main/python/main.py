import json
import requests.exceptions


def get_token_from_api(client_id, client_secret, username, password, token_url):
    try:
        payload = {'grant_type': 'password',
                   'username': username,
                   'password': password,
                   'scope': 'openid'}
        response = requests.post(token_url, data=payload, auth=(client_id, client_secret))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error invoking to obtain the token: {e}')
        return None


def call_get_api(api_url, api_params, api_type, token):
    try:
        if (api_type == 'id'):
            api_url += api_params
            api_params = ''
        api_call_headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}
        api_call_response = requests.get(api_url, params=api_params, headers=api_call_headers, timeout=300)
        api_call_response.raise_for_status()
        print(api_call_response.url)
        return api_call_response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error invoking API: {e}')
        return None


def main():
    # Read file with data for API connection...
    try:
        with open('data/authPRO.json') as f:
            conn_params = json.load(f)
    except FileNotFoundError as e:
        print(f'Connection configuration file not found... {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'Incorrect format of the connection configuration file... {e}')
        return None

    # Invoke the API authentication URL to get the token...
    connection_data = get_token_from_api(conn_params['client_id'], conn_params['client_secret'],
                                         conn_params['username'], conn_params['password'],
                                         conn_params['token_url'])

    # Read data API calls...
    try:
        with open('../../data/params_api.json') as f:
            api_call_params = json.load(f)
    except FileNotFoundError as e:
        print(f'API call configuration file not found... {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'Incorrect format of the API call configuration file... {e}')
        return None

    # API call using the obtained token...
    api_data = call_get_api(api_call_params['api1_url'],
                            api_call_params['api1_params'],
                            api_call_params['api1_type'],
                            connection_data['access_token'])
    print(api_data)

    # API call using the obtained token...
    api_data = call_get_api(api_call_params['api2_url'],
                            api_call_params['api2_params'],
                            api_call_params['api2_type'],
                            connection_data['access_token'])
    print(api_data)


if __name__ == "__main__":
    main()
