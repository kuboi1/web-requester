import requests
import time
import json
import os
from requests import Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from datetime import datetime


COLOR_OK = '\033[32m'       # Green
COLOR_ERR = '\033[31m'      # Red
COLOR_WAR = '\033[33m'      # Yellow
COLOR_MAG = '\033[95m'      # Magenta
COLOR_CYA = '\033[96m'     # Cyan
COLOR_DEFAULT = '\033[0m'   # White (reset)

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
REQUESTS_PATH = os.path.join(BASE_PATH, 'requests')
RESPONSES_PATH = os.path.join(BASE_PATH, 'responses')

KEY_RELOAD = 'r'
KEY_QUIT = 'q'

class Requester:
    _namespace: str
    _mode: str
    _url: str
    _settings: dict
    _requests: dict
    _common: dict

    def __init__(self, settings: dict) -> None:
        self._print_intro()

        self._settings = settings

        self._load_namespace()
        self._load_requests()
    
    def _load_namespace(self) -> None:
        namespaces = self._get_namespaces()

        if len(namespaces) == 0:
            self._print_err(f'No valid request json files found at \'{REQUESTS_PATH}\'')
            exit()
        
        # Pick from available namespaces if namespace not specified in settings
        self._namespace = self._settings['namespace'] if 'namespace' in self._settings else self._pick_namespace(namespaces)

        # Validate selected namespace
        if self._namespace not in self._get_namespaces().values():
            self._print_err(f'Invalid namespace \'{self._namespace}\'')
            exit()

    def _get_namespaces(self) -> dict:
        namespaces = {}
        for i, file in enumerate(os.listdir(REQUESTS_PATH)):
            if file.endswith('example'):
                continue
            namespaces[i - 1] = file.split(".")[0]
        
        return namespaces
    
    def _pick_namespace(self, namespaces: dict) -> str:
        print('Pick a namespace:')
        print()

        for i in namespaces:
            print(f' > {i}\t{COLOR_CYA}{namespaces[i]}{COLOR_DEFAULT}')
        
        self._print_extra_options()
        
        while True:
            namespace_num = input('> Namespace number: ')

            if namespace_num == KEY_RELOAD:
                self._reload_data(print_info=True)

            if namespace_num == KEY_QUIT:
                exit()

            if not namespace_num.isnumeric():
                self._print_war('Not a number')
                continue

            namespace_num = int(namespace_num)

            if namespace_num not in namespaces:
                self._print_war('Invalid namespace number')
                continue

            return namespaces[namespace_num]

    def _load_requests(self) -> dict:
        # Load namespace requests data
        with open(os.path.join(REQUESTS_PATH, f'{self._namespace}.json'), 'r') as f:
            data = json.load(f)
        
        mode = self._settings['mode']
        
        if mode not in data['url']:
            self._print_err(f'Missing url for mode \'{mode}\' in namespace \'{self._namespace}\'')
            exit()
        
        self._mode = mode
        self._url = data['url'][mode]
        self._requests = {key: data['requests'][key] for key in data['requests'] if 'mode' not in data['requests'][key] or data['requests'][key]['mode'] == mode}
        self._common = data['common'] if 'common' in data else {}

    def _send_request(self, request_name: str) -> Response:
        request = self._requests[request_name]

        # Add common request values
        request = self._add_common(request)

        target_link = f'{self._url}/{request["endpoint"]}'
        method = request['method']

        headers = request['headers'] if 'headers' in request else None
        id = request['id'] if 'id' in request else None
        params = request['parameters'] if 'parameters' in request else None
        body = request['body'] if 'body' in request else None
        basicAuth = request['basicAuth'] if 'basicAuth' in request else None

        # Send the request
        target_link = f'{target_link}/{id}' if id is not None else target_link

        url_params = '?' + '&'.join([f'{key}={params[key]}' for key in params]) if params != None else ''

        print()
        print(f'Sending {COLOR_MAG}{method}{COLOR_DEFAULT} {COLOR_CYA}{request_name}{COLOR_DEFAULT} request to: {target_link}{url_params}...')

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
                self._print_err(f'Unsupported method \'{method}\'')
                exit()

        return response

    def _save_response(self, request_name: str, response: Response) -> str:
        content_type = response.headers['Content-Type']
        datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        file_name = f'{request_name}_{datetime_str}'

        # Create a response directory for the namespace if not exist
        dir_path = (os.path.join(RESPONSES_PATH, self._namespace))
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        match content_type:
            case 'application/pdf':
                file_path = os.path.join(dir_path, f'{file_name}.pdf')
                with open(file_path, 'wb') as response_f:
                    response_f.write(response.content)
            case _:
                file_path = os.path.join(dir_path, f'{file_name}.json')
                response_data = self._create_json_response_data(response)
                with open(file_path, 'w') as response_f:
                    json.dump(response_data, response_f)
        
        return file_path
    
    def _create_json_response_data(self, response: Response) -> dict:
        try:
            response_content = response.json()
        except requests.exceptions.JSONDecodeError:
            self._print_war(f'Failed to json decode response content - using raw content instead')
            response_content = response.text

        if 'contentOnly' in self._settings and self._settings['contentOnly']:
            return response_content
        
        return {
            'status': response.status_code,
            'reason': response.reason,
            'headers': dict(response.headers),
            'content': response_content
        }

    def _add_common(self, request: dict) -> dict:
        for key in self._common:
            if key not in request:
                request[key] = self._common[key]
                continue

            for subkey in self._common[key]:
                if subkey not in request[key]:
                    request[key][subkey] = self._common[key][subkey]
        
        return request

    def _print_intro(self) -> None:
        print()
        print('-------------------')
        print('|  WEB REQUESTER  |')
        print('-------------------')
        print()
    
    def _print_extra_options(self) -> None:
        print()
        print(f' > {KEY_RELOAD}\t{COLOR_MAG}RELOAD{COLOR_DEFAULT}')
        print(f' > {KEY_QUIT}\t{COLOR_MAG}QUIT{COLOR_DEFAULT}')
        print()
    
    def _print_result(self, message: str, color: str = COLOR_DEFAULT) -> None:
        print()
        print(f'{color}{message}{COLOR_DEFAULT}')
        print()
    
    def _print_err(self, message: str) -> None:
        self._print_result(message, COLOR_ERR)
    
    def _print_war(self, message: str) -> None:
        self._print_result(message, COLOR_WAR)

    def _print_options(self) -> None:
        print(f'Requests for {COLOR_CYA}{self._namespace}{COLOR_DEFAULT} in {COLOR_MAG}{self._mode}{COLOR_DEFAULT} mode:')
        print()
        for i, name in enumerate(self._requests.keys()):
            method = self._requests[name]['method']
            endpoint = self._requests[name]['endpoint']
            id = self._requests[name]['id'] if 'id' in self._requests[name] else None

            option = f'{i}\t{COLOR_MAG}{method}{COLOR_DEFAULT} {COLOR_CYA}{name}{COLOR_DEFAULT}'
            url = f'{self._url}/{endpoint}{f"/{id}" if id is not None else ""}'

            print(f' > {option} => {url}')
        
        self._print_extra_options()
    
    def _reload_data(self, print_info: bool) -> None:
        self._load_namespace()
        self._load_requests()

        if print_info:
            self._print_result('Data reloaded')

    def _request(self, number: str) -> None:
        request_name = list(self._requests.keys())[number]

        # Reload requests if liveReload is set to true
        if 'liveReload' in self._settings and self._settings['liveReload']:
            self._reload_data(print_info=False)
            # Check if the selected request is still valid
            if not request_name in self._requests:
                self._print_war(f'Request \'{request_name}\' is no longer valid')
                return

        response = self._send_request(request_name)

        file_path = self._save_response(request_name, response)
        
        status = response.status_code
        reason = response.reason
        elapsed_ms = response.elapsed.total_seconds() * 1000

        status_color = COLOR_OK if response.ok else COLOR_ERR
        ms_color = COLOR_OK

        if elapsed_ms >= 20000:
            ms_color = COLOR_ERR
        elif elapsed_ms >= 5000:
            ms_color = COLOR_WAR

        print()
        print(f'Response returned with {status_color}{status} ({reason}) {COLOR_DEFAULT}in {ms_color}{elapsed_ms:.1f} ms{COLOR_DEFAULT}')
        print(f'Response file: {file_path}')
        print()
    
    def run(self) -> None:
        while True:
            self._print_options()

            request_number = input('> Request number: ')

            if request_number == KEY_RELOAD:
                self._reload_data(print_info=True)
                continue

            if request_number == KEY_QUIT:
                quit()

            if not request_number.isnumeric():
                self._print_war('Not a number')
                continue
            
            request_number = int(request_number)

            if request_number < 0 or request_number >= len(self._requests):
                self._print_war('Invalid request number')
                continue

            try:
                self._request(request_number)
            except ConnectionError as err:
                self._print_err(f'REQUEST FAILED WITH A CONNECTION ERROR:\n{err}')


def load_settings() -> dict:
    with open('settings.json', 'r', encoding='utf-8') as requests_f:
        return json.load(requests_f)


def main() -> None:
    settings = load_settings()

    requester = Requester(settings)

    requester.run()


if __name__ == '__main__':
    main()

