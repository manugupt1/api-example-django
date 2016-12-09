import requests, urllib
import json


class APIUtils:
    
    url = 'https://drchrono.com/api/'
    user = None
    def __init__(self, user):
        self.user = user
        access_token = user.social_auth.get(user = user).extra_data['access_token']
        self.headers = {'Authorization': 'Bearer {0}'.format(access_token)}
        self.headers['Content-Type'] = 'application/json'

    def build_url(self, endpoint, id):
        final_url = self.url+ endpoint
        if id is not None:
            final_url += '/' + str(id)
        return final_url

    def get(self, params, endpoint, id = None):
        url = self.build_url(endpoint, id)
        data = requests.get(url, params = params, headers = self.headers).json()
        return data

    def patch(self, params, endpoint, id):
        url = self.build_url(endpoint, id)
        data = requests.patch(url, data = json.dumps(params), headers = self.headers)
        return data

    def put(self, params, endpoint, id):
        url = self.build_url(endpoint, id)
        print url
        data = requests.put(url, data = json.dumps(params), headers = self.headers)
        return data

    def get_user_id(self):
        return self.user.social_auth.get(user = self.user).uid


