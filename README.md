# Web Requester

## Usage

* Sends requests to specified endpoints

### Requests
* Requests are specified in the **requests/** directory
* Requests are seperated into **namespaces**
* Each namespace has it's own json config file in format *{namespace}.json*
* Example of such file is included in the repository (*requests/namespace.json.example*)
* Each request has it's own name

### Responses
* Requester currently supports *.json* and *.pdf* responses
* Responses are saved into the **responses/** directory in *{datetime}\_{namepsace}\_{request_name}.{ext}* format

### Settings
* Settings are specified in a **settings.json** file
* Example of such file is included in the repository (*settings.json.example*)
* There are 2 settings you can specify:
    * *mode* [required] - specifies the mode with which the app should start (PROD|DEV|LOCAL)
    * *namespace* [optional] - Specifies the namespace which the app should load on start (if not present, you will be promted to pick one of the available namespaces)

## Dependencies
* [Python 3.10+](https://www.python.org/downloads/)
* **requests** Python package (`pip install requests`)