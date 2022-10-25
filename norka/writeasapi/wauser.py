import requests
import json
from .uri import URI, ME_URI

import code

class user(object):
    def __init__(self):
        pass

    def auth(self, user, password):
    # This is how you will authenticate your Write.as account and retrieve an access token for future requests
        data = {"alias": user, "pass": password }

        r = requests.post(URI, data=json.dumps(data),
                            headers={"Content-Type":"application/json"})

    #
        if r.status_code != 200:
            return "Error in login(): %s" % r.json()["error_msg"]

        else:
            user = r.json()["data"]
            return user

    def authout(self, token):
        r = requests.delete("https://write.as/api/auth/me",
                headers={"Authorization": "Token %s" % token})

        if r.status_code != 204:
            return "Error in logout(): %s" % r.json()["error_msg"]

        else:
            return "You are logged out!"

    def getPosts(self, token):
        p = requests.get(ME_URI + "/posts",
            headers={"Authorization":"Token %s" % token,
                "Content-Type":"application/json"})

        if p.status_code != 200:
            return "Error in retrievePosts(): %s" % p.json()["error_msg"]

        else:
            uposts = p.json()["data"]
            return uposts

    def getCollections(self, token):
        c = requests.get(ME_URI + "/collections",
            headers={"Authorization":"Token %s" % token,
                "Content-Type":"application/json"})

        if c.status_code != 200:
            return "Error in retrieveCollections(): %s" % c.json()["error_msg"]

        else:
            ucollections = c.json()["data"]
            return ucollections

    def getChannels(self, token):
        c = requests.get(ME_URI + "/channels",
            headers={"Authorization":"Token %s" % token,
                "Content-Type":"application/json"})

        if c.status_code != 200:
            return "Error in retrieveChannels(): %s" % c.json()["error_msg"]

        else:
            uchannels = c.json()["data"]
            return uchannels
