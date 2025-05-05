# medium.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import Enum

import requests
from loguru import logger

from norka.models.document import Document


class PublishStatus(Enum):
    PUBLIC = 'public'
    DRAFT = 'draft'
    UNLISTED = 'unlisted'


class Medium:
    BASE_API_URL = 'https://api.medium.com/v1'

    def __init__(self, access_token: str = None):
        self.access_token = None
        self.session = requests.Session()
        self.set_token(access_token)

    def api_route(self, path: str) -> str:
        return f'{self.BASE_API_URL}{path}'

    def set_token(self, access_token: str):
        self.access_token = access_token
        self.session.headers.update(dict(Authorization=f'Bearer {self.access_token}'))

    def get_user(self):
        try:
            response = self.session.get(self.api_route('/me'))
            if response.status_code == 200:
                return response.json().get('data')
            return None
        except Exception as e:
            logger.error(e)
            return None

    def create_post(self, user_id: str, document: Document, publish_status: PublishStatus = None):
        response = self.session.post(
            self.api_route(f'/users/{user_id}/posts'),
            json={
                "title": document.title,
                "content": document.content,
                "contentFormat": "markdown",
                "publishStatus": publish_status.value
            }
        )
        if response.status_code == 201:
            return response.json().get('data')

        return None
