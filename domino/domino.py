from .routes import _Routes

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import json
import os
import logging
import requests


class Domino:
    def __init__(self, project, api_key=None, host=None):
        self._configure_logging()

        if host is not None:
            host = host
        elif 'DOMINO_API_HOST' in os.environ:
            host = os.environ['DOMINO_API_HOST']
        else:
            raise Exception("Host must be provided, either via the constructor value or through DOMINO_API_HOST environment variable.")

        self._logger.info('Initializing Domino API with host ' + host)

        owner_username = project.split("/")[0]
        project_name = project.split("/")[1]
        self._routes = _Routes(host, owner_username, project_name)

        self._api_key = api_key

        if 'DOMINO_USER_API_KEY' in os.environ:
            self._api_key = os.environ['DOMINO_USER_API_KEY']
        elif api_key is not None:
            self._api_key = api_key
        else:
            raise Exception("API key must be provided, either via the constructor value or through DOMINO_USER_API_KEY environment variable.")

    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    def runs_list(self):
        url = self._routes.runs_list()
        return self._get(url)

    def runs_start(self, command, isDirect=False, commitId=None, title=None, tier=None, publishApiEndpoint=None):
        url = self._routes.runs_start()

        request = {
            "command": command,
            "isDirect": isDirect,
            "commitId": commitId,
            "title": title,
            "tier": tier,
            "publishApiEndpoint": publishApiEndpoint
        }

        response = requests.post(url, auth=('', self._api_key), json=request)
        return response.json()

    def files_list(self, commitId, path='/'):
        url = self._routes.files_list(commitId, path)
        return self._get(url)

    def files_upload(self, path, file):
        url = self._routes.files_upload(path)
        return self._put_file(url, file)

    def blobs_get(self, key):
        url = self._routes.blobs_get(key)
        return self._open_url(url)

    def fork_project(self, target_name):
	url = self._routes.fork_project()
	request = { "overrideProjectName" : target_name }
	response = requests.post(url, auth=('', self._api_key), data=request)
	return response.status_code

    def endpoint_state(self):
        url = self._routes.endpoint_state()
        return self._get(url)

    def endpoint_unpublish(self):
        url = self._routes.endpoint()
        response = requests.delete(url, auth=('', self._api_key))
        return response

    def endpoint_publish(self, file, function, commitId):
        url = self._routes.endpoint_publish()

        request = {
            "commitId": commitId,
            "bindingDefinition": {
                "file": file,
                "function": function
            }
        }

        response = requests.post(url, auth=('', self._api_key), json=request)
        return response

    def _get(self, url):
        return requests.get(url, auth=('', self._api_key)).json()

    def _put_file(self, url, file):
        return requests.put(url, data=file, auth=('', self._api_key))

    def _open_url(self, url):
        password_mgr = urllib.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self._routes.host, '', self._api_key)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        return opener.open(url)
