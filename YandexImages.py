# -*- coding: utf-8 -*-
import json
import pprint
import time
from urllib.parse import urlparse

import requests
from requests import HTTPError


class YandexImages(object):
    def __init__(self):
        self.SESSION = requests.Session()
        # self.SESSION.headers.update(AUTH_HEADER)

        self.API_VERSION = 'v1'
        self.API_BASE_URL = 'https://dialogs.yandex.net/api/'
        self.API_URL = self.API_BASE_URL + self.API_VERSION + '/'
        self.skills = '3f93126a-c42a-406d-bb04-086f2abe14d8'

    def set_auth_token(self, token):
        self.SESSION.headers.update(self.get_auth_header(token))

    def get_auth_header(self, token):
        return {
            'Authorization': 'OAuth %s' % token
        }

    def log(self, error_text, response):
        log_file = open('YandexApi.log', 'a')
        log_file.write(error_text+'\n')#+response)
        log_file.close()

    def validate_api_response(self, response, required_key_name=None):
        content_type = response.headers['Content-Type']
        content = json.loads(response.text) if 'application/json' in content_type else None

        if response.status_code == 200:
            if required_key_name and required_key_name not in content:
                self.log('Unexpected API response. Missing required key: %s' % required_key_name, response=response)
                return None
        elif content and 'error_message' in content:
            self.log('Error API response. Error message: %s' % content['error_message'], response=response)
            return None
        elif content and 'message' in content:
            self.log('Error API response. Error message: %s' % content['message'], response=response)
            return None
        else:
            response.raise_for_status()

        return content

    ################################################
    # Проверить занятое место                      #
    #                                              #
    # Вернет массив                                #
    # - total - Сколько всего места осталось       #
    # - used - Занятое место                       #
    ################################################
    def checkOutPlace(self):
        result = self.SESSION.get(self.API_URL+'status')
        content = self.validate_api_response(result)
        if content is not None:
            return content['images']['quota']
        return None

    ################################################
    # Загрузка изображения из интернета            #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################
    def downloadImageUrl(self, url):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL+path, data=json.dumps({"url": url}))
        content = self.validate_api_response(result)
        if content is not None:
            return content['image']
        return None


    ################################################
    # Загрузка изображения из файла                #
    #                                              #
    # Вернет массив                                #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.               #
    ################################################

    def downloadImageFile(self, img):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL+path, files={'file': (img, open(img, 'rb'))})
        content = self.validate_api_response(result)
        if content is not None:
            return content['image']
        return None


    def downloadImageImage(self, img):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.post(url=self.API_URL+path, files={'file': ('first.jpg', img)})
        content = self.validate_api_response(result)
        if content is not None:
            return content['image']
        return None

    ################################################
    # Просмотр всех загруженных изображений        #
    #                                              #
    # Вернет массив из изображений                 #
    # - id - Идентификатор изображения             #
    # - origUrl - Адрес изображения.	           #
    ################################################
    def getLoadedImages(self):
        path = 'skills/{skills_id}/images'.format(skills_id=self.skills)
        result = self.SESSION.get(url=self.API_URL+path)
        content = self.validate_api_response(result)
        if content is not None:
            return content['images']
        return None

    ################################################
    # Удаление выбранной картинки                  #
    #                                              #
    # В случае успеха вернет 'ok'	               #
    ################################################
    def deleteImage(self, img_id):
        path = 'skills/{skills_id}/images/{img_id}'.format(skills_id=self.skills, img_id=img_id)
        result = self.SESSION.delete(url=self.API_URL+path)
        content = self.validate_api_response(result)
        if content is not None:
            return content['result']
        return None

    def deleteAllImage(self):
        success = 0
        fail = 0
        images = self.getLoadedImages()
        for image in images:
            image_id = image['id']
            if image_id:
                if self.deleteImage(image_id):
                    success += 1
                else:
                    fail += 1
            else:
                fail += 1

        return {'success': success, 'fail': fail}

# yandex = YandexImages()
# yandex.set_auth_token(token = 'AgAAAAAqHEs_AAT7o7tmP0cMDkczmxBtEz1jnOM')
# yandex.skills = '1a944d0d-9044-40ea-b751-7b54cc47b1ed'
# print(yandex.checkOutPlace())
# print(yandex.downloadImageUrl('https://www.example.ru/test.png'))
#print (yandex.getLoadedImages())
