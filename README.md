# 📡 Web Requester

## 🛠️ Usage

* Sends HTTP requests to specified endpoints on the web

### 🚀 Quick Start
* Run using poetry (preffered)
    1. Open console
    2. Move into the web-requester directory `cd /path/to/web-requester`
    3. Install dependencies `poetry install`
    4. Run the app `poetry run python requester.py`
* Run without poetry (alternative)
    1. Open console
    2. Move into the web-requester directory `cd /path/to/web-requester`
    3. Install the requests package `pip install requests`
    4. Run the app using `python requester.py`

### 🧾 Requests
* Requests are specified in the **requests/** directory
* Requests are seperated into **namespaces**
* Each namespace has it's own json config file in format *{namespace}.json*
* Example of such file is included in the repository (*requests/namespace.json.example*)
* Each request has it's own name
* The *"common"* values are sent with each request

### 📄 Responses
* Requester currently supports *.json* and *.pdf* responses
* Responses are saved into the **responses/*{namespace}*** directory in *{request_name}-{status}\_\_{datetime}.{extension}* format

### ⚙️ Settings
* Settings are specified in the **settings.json** file
* Example of such file is included in the repository (*settings.json.example*)
* There are 4 settings you can specify:
    * *mode* [**required**] - Specifies the mode with which the app should start (PROD|DEV|LOCAL for example, but you can add as many as you want)
    * *namespace* [optional] - Specifies the namespace which the app should load on start (if not present, you will be promted to pick one of the available namespaces)
    * *contentOnly* [optional|default: false] - Specifies if the status, reason and headers of the response should be saved or just the body content (Works for *.json* responses only)
    * *liveReload* [optional|default: false] - Specifies if the requests file should be reloaded on each request sent. This allows for editing the requests in the json file without restarting the program (might cause some slight performance issues with large json files)

### ⚡ Actions
* 📡 **Request number** (eg. 1) - Sends the request corresponding to that number
* 🔄 **RELOAD** - Reloads the requests file, loading any changes made while the app was running
* 🧹 **CLEAR RESPONSES** - Clears the *responses/{namespace}* directory
* 👋 **QUIT** - Exits the app

## 🔗 Dependencies
* **[Python 3.10+](https://www.python.org/downloads/)**
* **[Poetry](https://python-poetry.org/)** for dependency management or the **[requests](https://pypi.org/project/requests/)** Python package directly