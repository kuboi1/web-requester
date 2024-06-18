import requests
import time
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime

MODE_PRODUCTION = 'PROD'
MODE_DEV = 'DEV'
MODE_LOCAL = 'LOCAL'

COLOR_OK = '\033[32m'       # Green
COLOR_ERR = '\033[31m'      # Red
COLOR_WAR = '\033[33m'      # Yellow
COLOR_DEFAULT = '\033[0m'   # White (reset)


class Requester:
    namespace: str
    mode: str
    url: str
    requests: dict

    def __init__(self, settings: dict) -> None:
        self._load_requests(settings['mode'], settings['namespace'])

    def _load_requests(self, mode: str, namespace: str) -> dict:
        with open('requests.json', 'r', encoding='utf-8') as requests_f:
            data = json.load(requests_f)

        if namespace not in data:
            print(f'{COLOR_ERR}Invalid namespace \'{namespace}\'{COLOR_DEFAULT}')
            exit()
        
        if mode not in [MODE_PRODUCTION, MODE_DEV, MODE_LOCAL]:
            print(f'{COLOR_ERR}Invalid mode \'{mode}\'{COLOR_DEFAULT}')
            exit()
        
        if mode not in data[namespace]['url']:
            print(f'{COLOR_ERR}Missing url for mode \'{mode}\'{COLOR_DEFAULT}')
            exit()
        
        self.namespace = namespace
        self.mode = mode
        self.url = data[namespace]['url'][mode]
        self.requests = data[namespace]['requests']

    def print_intro(self) -> None:
        print('---------')
        print('REQUESTER')
        print('---------')

    def print_options(self) -> None:
        print(f'Requests for {self.namespace} in {self.mode} mode:')
        for i, name in enumerate(self.requests.keys()):
            print(f' > {i} {name}: {self.requests[name]["method"]} => {self.url}/{self.requests[name]["endpoint"]}')
        print()
        print(' > q: QUIT')
        print()

    def send_request(self, number: str) -> None:
        request_name = list(self.requests.keys())[number]
        request = self.requests[request_name]

        target_link = f'{self.url}/{request["endpoint"]}'
        method = request['method']
        headers = request['headers']

        params = request['parameters'] if 'parameters' in request else None
        body = request['body'] if 'body' in request else None
        basicAuth = request['basicAuth'] if 'basicAuth' in request else None

        #Send the request
        print()
        print(f'Sending {method} request {request_name} to: {target_link}...')

        start_time = time.time()

        match method:
            case 'GET':
                response = requests.get(
                    target_link, 
                    params=params,
                    headers=headers,
                    auth=HTTPBasicAuth(basicAuth['username'], basicAuth['password']) if basicAuth is not None else None
                )
            case 'POST':
                response = requests.post(
                    target_link, 
                    params=params, 
                    headers=headers,
                    json=body, 
                    auth=HTTPBasicAuth(basicAuth['username'], basicAuth['password']) if basicAuth is not None else None
                )
            case 'PUT':
                response = requests.put(
                    target_link, 
                    params=params, 
                    headers=headers,
                    json=body, 
                    auth=HTTPBasicAuth(basicAuth['username'], basicAuth['password']) if basicAuth is not None else None
                )
            case _:
                print(f'{COLOR_ERR}Unsupported method \'{method}\'{COLOR_DEFAULT}')
                exit()

        end_time = time.time()

        # Save the response
        datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(f'responses/{datetime_str}_{self.namespace}_{request_name}.json', 'wb') as response_f:
            response_f.write(response.content)

        status = response.status_code
        reason = response.reason

        ms = (int) ((end_time - start_time) * 1000)

        status_color = COLOR_OK if status == 200 else COLOR_ERR
        ms_color = COLOR_OK

        if ms >= 20000:
            ms_color = COLOR_ERR
        elif ms >= 5000:
            ms_color = COLOR_WAR

        print(f'Response returned with {status_color}{status} ({reason}) {COLOR_DEFAULT}in {ms_color}{ms} ms{COLOR_DEFAULT}')


def load_settings() -> dict:
    with open('settings.json', 'r', encoding='utf-8') as requests_f:
        return json.load(requests_f)


def main() -> None:
    settings = load_settings()

    requester = Requester(settings)
    
    requester.print_intro()

    while True:
        print()
        requester.print_options()

        request_number = input('> Request number: ')

        if request_number == 'q':
            break

        if not request_number.isnumeric():
            print(f'{COLOR_WAR}Not a number{COLOR_DEFAULT}')
            continue
        
        request_number = int(request_number)

        if request_number < 0 or request_number >= len(requester.requests):
            print(f'{COLOR_WAR}Invalid request number{COLOR_DEFAULT}')
            continue

        requester.send_request(request_number)


if __name__ == '__main__':
    main()

