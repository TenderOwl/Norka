import requests
import json
from .uri import RWA_URI

class rwa(object):
    def get(self, skip=0):

        params = {"skip": skip}

        p = requests.get(RWA_URI, params=params)

        if p.status_code != 200:
            return "Error in rwa(): %s" % p.json()["error_msg"]

        else:
            posts = p.json()["data"]
            return posts
