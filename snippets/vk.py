import vk
import requests
import os

class Vk:
    def __init__(self):
        self.v = '6.0.0'
        self.auth()

    def auth(self):
        with open('config.txt', 'r') as f:
            info = eval(f.read())
            self.group_id = info['vk']['group_id']
            access_token = info['vk']['access_token']
        
        if access_token == '':
            client_id = input('Write your client id: ')
            access_token = input(f'Write access token from url bar: https://oauth.vk.com/authorize?client_id={client_id}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,groups,photos,offline&response_type=token \n')
            
            with open('config.txt', 'r+') as f:
                info = eval(f.read())
                info['vk']['access_token'] = access_token
                f.write(str(info))
        
        session = vk.Session(access_token=access_token)
        self.api = vk.API(session)

    def post(self, **kwargs):
        if 'image_url' in kwargs.keys():
            destination = self.api.photos.getWallUploadServer(group_id=self.group_id, v=self.v)

            image = requests.get(kwargs['image_url'], stream=True)
            data = ("image.jpg", image.raw, image.headers['Content-Type'])
            meta = requests.post(destination['upload_url'], files={'photo': data}).json()
            photo = self.api.photos.saveWallPhoto(group_id=self.group_id, **meta, v=self.v)[0]

            try:
                kwargs['attachments'] += f",photo{photo['owner_id']}_{photo['id']}"
            except:
                kwargs['attachments'] = f"photo{photo['owner_id']}_{photo['id']}"
            
            del kwargs['image_url']

        self.api.wall.post(
            owner_id = -self.group_id, 
            v = self.v,
            **kwargs
            )
