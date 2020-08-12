import requests
import json
from .uri import COLL_URI

class collection(object):
    def get(self, alias):
        c = requests.get(COLL_URI + "/%s" % alias,
                headers={"Content-Type": "application/json"})

        if c.status_code != 200:
            return "Error in retrieveCollection(): %s" % c.json()["error_msg"]

        else:
            collection = c.json()["data"]
            return collection


    def create(self, token, alias, title):

        data = {"alias": alias,
                "title": title }

        c = requests.post(COLL_URI, data=json.dumps(data),
                        headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if c.status_code != 201:
            return "Error in createCollection(): %s" % c.json()["error_msg"]

        else:
            collection = c.json()["data"]
            return collection

    def delete(self, token, alias):
        c = requests.delete(COLL_URI + "/%s" % alias,
                headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if c.status_code != 204:
            return "Error in deleteCollection(): Invalid token or collection."

        else:
            return "Collection deleted!"

    def getP(self, alias, slug):
        p = requests.get(COLL_URI + "/%s/posts/%s" % (alias, slug),
            headers={"Content-Type": "application/json"})

        if p.status_code != 200:
            return "Error in retrieveCPost(): %s" % c.json()["error_msg"]

        else:
            cpost = p.json()["data"]
            return cpost

    def getPs(self, alias, page=1):
        p = requests.get(COLL_URI + "/%s/posts" % alias,
                            params={'page': page})

        if p.status_code != 200:
            return "Error in retrieveCPosts(): %s" % c.json()["error_msg"]

        else:
            cposts = p.json()["data"]
            return cposts

    def createP(self, token, alias, body, title=None, **kwargs):

        d = {"body": body,
            "title": title}

        k = kwargs

        data = {**d, **k}

        p = requests.post(COLL_URI + "/%s/posts" % alias, data=json.dumps(data),
            headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if p.status_code != 201:
            return "Error in createCPost(): %s" % p.json()["error_msg"]

        else:
            cpost = p.json()["data"]
            return cpost

    def claimP(self, token, alias, id):

        data = [{"id": id}]

        p = requests.post(COLL_URI + "/%s/collect" % alias, data=json.dumps(data),
            headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if p.status_code != 200:
            return "Error in claimCPost(): %s" % p.json()["error_msg"]

        else:
            post = p.json()["data"]
            return post

    def pin(self, token, alias, id, position=1):

        data = [{"id": id,
                "position": position,}]

        p = requests.post(COLL_URI + "/%s/pin" % alias, data=json.dumps(data),
            headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if p.status_code != 200:
            return "Error in pinPost(): %s" % p.json()["error_msg"]

        else:
            post = p.json()["data"]
            return post

    def unpin(self, token, alias, id):

        data = [{"id": id}]

        p = requests.post(COLL_URI + "/%s/unpin" % alias, data=json.dumps(data),
            headers={"Authorization": "Token %s" % token,
                        "Content-Type": "application/json"})

        if p.status_code != 200:
            return "Error in unpinPost(): %s" % p.json()["error_msg"]

        else:
            post = p.json()["data"]
            return post
