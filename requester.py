import requests
import time
import json

PRODUCTION = False
LOCAL = True

PARAMS = '_tracy_skip_error'

COLOR_OK = '\033[32m'       # Green
COLOR_ERR = '\033[31m'      # Red
COLOR_WAR = '\033[33m'      # Yellow
COLOR_DEFAULT = '\033[0m'   # White (reset)

if __name__ == '__main__':
    request_type = input('Request type: ')

    # Load requests data
    with open('requests.json', 'r', encoding='utf-8') as requests_f:
        requests_data = json.load(requests_f)

    if request_type not in requests_data['requests']:
        print(f'{COLOR_ERR}Invalid request type \'{request_type}\'{COLOR_DEFAULT}')
        exit()
    
    request = requests_data['requests'][request_type]
    
    # Set base url
    if PRODUCTION:
        base_url = requests_data['url']['prod']
    elif LOCAL:
        base_url = requests_data['url']['local']
    else:
        base_url = requests_data['url']['dev']
    
    target_link = base_url + request['target']
    request_body = request['body']

    # Set common request data
    request_body['data']['ApiKey'] = requests_data['params']['apiKey']
    request_body['data']['ResellerId'] = requests_data['params']['resellerId']
    request_body['data']['SupplierId'] = requests_data['params']['supplierId']

    #Send the request
    print(f'Sending request to: {target_link}...')

    start_time = time.time()
    response = requests.post(target_link, json=request_body, params=PARAMS)
    end_time = time.time()

    # Save the response
    with open('response.json', 'wb') as response_f:
        response_f.write(response.content)

    status = response.status_code
    reason = response.reason

    ms = (int) ((end_time - start_time) * 1000)

    status_color = COLOR_OK if status == 200 else COLOR_ERR
    ms_color = COLOR_OK

    if ms >= 2000:
        ms_color = COLOR_WAR
    elif ms >= 5000:
        ms_color = COLOR_ERR

    print(f'Response returned with {status_color}{status} ({reason}) {COLOR_DEFAULT}in {ms_color}{ms} ms{COLOR_DEFAULT}')

