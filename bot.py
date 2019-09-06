from snippets.reddit import Reddit
from snippets.vk import Vk

import asyncio
import time


def auth():
    """
    Authentication in reddit app and vk app
    """
    with open('config.txt', 'r+') as f:
        try:
            info = eval(f.read())
        except:
            f.write(str(
                {'vk': {'access_token': '','group_id': 0},
                'reddit': {'client_id': '', 'client_secret': '', 'user_agent': ''}}
                ))
        
            raise Exception('Fill in the information in config.txt (if you don\'t know the access_token, you can leave this field blank.')

    try:
        vk = Vk()
        r = Reddit(
            client_id = info['reddit']['client_id'],
            client_secret = info['reddit']['client_secret'], 
            user_agent = info['reddit']['user_agent'] 
        )
    except:
        raise 'Wrong information in config.txt'

    return vk, r


def content_filter(text):
    """
    The simple filter of words
    Change the values in filter.txt to configurate it.
    """
    filter_result = {
        'length': True,
        'count': True,
        'black_list': True
    }
    
    with open('filter.txt', 'r') as f:
        info = eval(f.read())
    
    if len(text) < info['min_word_length'] or len(text) > info['max_word_length']:
        filter_result['length'] = False
    
    if len(text.split(' ')) < info['min_count_of_words'] or len(text.split(' ')) > info['max_count_of_words']:
        filter_result['count'] = False

    for word in info['black_list']:
        if word in text:
            filter_result['black_list'] = False
        break
    
    return filter_result


async def create_new_posts(vk, r, settings):
    data = r.get_posts_from(**settings['reddit'])
    while True:
        new_posts = r.get_new_posts_from_array(data, **settings['reddit'])
        print(f"Поиск в {settings['reddit']['name']}")
        for post in new_posts:
            print(f"Новый пост в {settings['reddit']['name']}\n{post}")
            result = content_filter(post['title'])
            print(f"Фильтр: {result}")
            if result['count'] == True and result['length'] == True:
                if result['black_list'] != False: post['title'] = ''
                try:
                    vk.post(
                        message = post['title'], 
                        image_url = post['url'],
                        **settings['vk']
                    )
                except Exception as e:
                    print('Невозможно сделать запись: '+e)
            data = r.get_posts_from(**settings['reddit'])
        
        await asyncio.sleep(settings['delay'])


def main():
    vk, r = auth()

    with open('search_settings.txt','r') as f:
        settings = []
        for stroke in f.read().split('\n'):
            setting = eval(stroke)
            try:
                setting['vk']['publish_date'] = time.time() + setting['delay'] + setting['vk']['publish_delay']
                del setting['vk']['publish_delay']
            except: pass
            
            settings.append(setting)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(*[create_new_posts(vk, r, setting) for setting in settings])
    )
    loop.close()


if __name__ == '__main__':
    main()