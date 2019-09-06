import praw
from time import sleep

class Reddit:
    def __init__(self, **kwargs):
        self.reddit = praw.Reddit(**kwargs)

    def get_front_page(self):
        data = [{
            'title': post.title,
            'body': post.selftext,
            'url': post.url,
            'created_at': post.created
            } for post in self.reddit.get_front_page()]
        
        return data

    def get_posts_from(self, name, **mode):
        if mode['sort'] in ['hot', 'new', 'rising']:
            posts = eval(f"self.reddit.get_subreddit(name).get_{mode['sort']}(limit={mode['limit']})")
        elif mode['sort'] in ['top', 'controversial']:
            #ingenious solution from the 'praw' creators to make a new function for each period
            posts = eval(f"self.reddit.get_subreddit(name).get_{mode['sort']}_from_{mode['period']}()")
        else:
            return

        data = [{
            'title': post.title,
            'body': post.selftext,
            'url': post.url,
            'created_at': post.created
            } for post in posts]

        return data

    def get_new_posts_from_array(self, data, name, **mode):
        new_data = self.get_posts_from(name, **mode)
        
        new_posts = []
        for post in new_data:
            if post not in data:
                new_posts.append(post)
        
        return new_posts
    
    def get_latest_posts(self, name, data, attach=False, **mode):
        new_data = self.get_posts_from(name, **mode)
        dpost = 1 if attach else 0

        if data[dpost] in new_data:
            index = new_data.index(data[dpost])
            if index != dpost:
                return [post for post in new_data[:index]]
