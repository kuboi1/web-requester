# Web Requester

## Usage

* Sends requests to specified websites

### Requests
* Request are specified in the **requests.json** file
* Example of such file is included in the repository
* Requests are seperated into **namespaces**
* Each request has it's own name

### Responses
* Whatever json body content is returned is saved into a .json file
* The responses are saved into the responses/ directory in *<datetime\>\_<namepsace\>\_<request_name>* format

### Settings
* Settings are specified in a **settings.json** file
* Example of such file is included in the repository
* There are 2 settings you can specify:
    * *mode* - specifies the mode with which the app should start (PROD|DEV|LOCAL)
    * *namespace* - Specifies the namespace which the app should load on start

## Dependencies
* [Python 3.10+](https://www.python.org/downloads/)
* **requests** Python package (`pip install requests`)