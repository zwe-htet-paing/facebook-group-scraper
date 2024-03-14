import urllib.request
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import time
import re
import datetime
import logging
import pickle
import sys

from custom_utils import parse_datetime
import utils.tag_config as tag

class Extractor:
    def __init__(self):
        pass
    
    @staticmethod
    def format_date(date_string):
        if date_string is None:
            return None

        formatted_date = parse_datetime(date_string)
        return formatted_date

    @staticmethod
    def get_post_url(r):    
        # posts_tag = 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm'
        post_element = r.find('a', {'class':tag.posts_tag})
        if post_element is not None:
            post_url = post_element.get('href')
        else:
            post_url = None
        
        return post_url
    
    @staticmethod
    def get_user(r):    
        # user_tag = 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f'
        user_element = r.find('a',{'class':tag.user_tag})
        
        #@ username
        if user_element is not None:
            username = user_element.get_text().strip()
            
            #@ user_id
            user_id = user_element.get('href')[25:].split('?')[0]
            if user_id == 'profile.php':
                user_id = user_element.get('href').split('?id=')[1].split('&')[0]
            
        else:
            #@ anonymous user
            # user_element = r.find('div', {'class':user_tag})
            # username = user_element.get_text().strip()
            username = 'None'
            user_id = 'None'
            
        return user_id, username
    
    @staticmethod
    def get_text(r):
        # text_tag = 'x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h'
        text_element = r.find('span',{'class':tag.text_tag})        
        if text_element is not None:
            text = text_element.get_text().strip()
        else:
            text_element = r.find('div',{'class':tag.text_tag1})
            if text_element is not None:
                text = text_element.get_text().strip()
            else:
                text_element = r.find('div', {'class':tag.text_tag2})
                text = text_element.get_text().strip() if text_element is not None else ''
        
        return text
    
    @staticmethod
    def get_shared_post(r):
        # share_post_tag = 'x1jx94hy x8cjs6t x1ch86jh x80vd3b xckqwgs x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x178xt8z xm81vs4 xso031l xy80clv xfh8nwu xoqspk4 x12v9rci x138vmkv x6ikm8r x10wlt62 x16n37ib xq8finb'     
        shared_post = r.find('div', {'class':tag.shared_post_tag})
        
        return shared_post
    
    @staticmethod
    def get_shared_text(r):
        shared_text_element = r.find('div',{'class':tag.shared_text_tag})
        if shared_text_element is not None:
            shared_text = shared_text_element.get_text().strip()
        else:
            shared_text = ''
            
        return shared_text
        
    @staticmethod
    def get_date_string(r, page):
        # 1. Using <a> tag
        date_element = r.find('a',{'class':tag.date_tag})
        date_string = date_element.get_text().strip() if date_element else None
        # print("Date element: ", date_element)
        # print("Date string: ", date_string)
        
        if (date_string == '' or date_string is None) and date_element is not None:
            span_element = date_element.find('span', {'class':tag.span_date_tag})
            if span_element is not None:
                # print('<use> tag')
                # 2. Using <use> tag
                use_element = span_element.find('use')
                date_index = use_element['xlink:href'] if use_element is not None else None
                date_element = page.find('text', {'id':str(date_index)}) if date_index is not None else None
                if date_element is None:
                    # print('aria-labelledby')
                    # 3. Using "aria-labelledby" attribute
                    date_index = span_element['aria-labelledby']
                    date_element = page.find('span', {'id':str(date_index)})
                    if date_element is None:
                        # print('svg')
                        # 4. Using "svg" attribute
                        svg_element = span_element.find('use')
                        date_index = svg_element['xlink:href'] if svg_element is not None else None
                        svg_date_element = page.find('svg', {'id': str(date_index[1:])}).find('use') if date_index is not None else None
                        svg_date_index = svg_date_element['xlink:href'] if svg_date_element is not None else None
                        # print(svg_date_index)
                        date_element = page.find('text', {'id':str(svg_date_index[1:])}) if svg_date_index is not None else None
                    
                date_string = date_element.text if date_element is not None else None
                # print(date_string)
        
        return date_string
    
    @staticmethod
    def write_csv(df, filename):
        df.to_csv(filename, index=False)
    
    @staticmethod
    def get_images(r):
        #@ images
        # image_tag='xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3'
        image_element=r.find_all('img', {'class':tag.image_tag})
        
        # image_tag1='x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3 xl1xv1r'
        image_element1=r.find_all('img', {'class':tag.image_tag1})
        

        temp_images = []
        if image_element is not None:
            for image in image_element:
                temp_images.append(image['src'])
                
        if image_element1 is not None:
            for image in image_element1:
                temp_images.append(image['src'])
                
        return temp_images
    
    @staticmethod
    def write_csv(df, filename):
        df.to_csv(filename, index=False)
    
    def extract_data(self, page_source=None, source_file=None):
        if page_source is not None:  
            page = bs(page_source, 'lxml')
        else:
            with open(source_file, "r", encoding="utf-8") as file:
                f = file.read()
            page = bs(f, 'lxml')

        group_posts = page.find_all('div', {
            'class': tag.post_list_tag
                                    })
        
        #@ entities
        self.post_urls = []
        self.user_ids = []
        self.usernames = []
        self.post_texts = []
        self.dates = []

        self.shared_post_urls = []
        self.shared_user_ids = []
        self.shared_usernames = []
        self.shared_texts = []
        self.shared_dates = []

        self.images = []
        
        for idx, r in enumerate(group_posts[1:]):
            
            #@ POST URL
            post_url = self.get_post_url(r)
            self.post_urls.append(post_url)

            #@ USER ID and USERNAME
            user_id, username = self.get_user(r)
            self.user_ids.append(user_id)
            self.usernames.append(username)
            
            #@ TEXT
            text = self.get_text(r)
            self.post_texts.append(text)
            
            #@ DATE
            date_string = self.get_date_string(r, page)
            formatted_date = self.format_date(date_string)
            self.dates.append(formatted_date)
            
            #@ SHARED POST
            shared_post = self.get_shared_post(r)
            if shared_post is not None:
                
                #@ shared post_url
                shared_post_url = self.get_post_url(shared_post)
            
                #@ shared user id and username
                shared_user_id, shared_username = self.get_user(shared_post)         
                
                #@ shared text
                shared_text = self.get_shared_text(shared_post)
                 
                #@ shared date
                date_string = self.get_date_string(r, page) 
                shared_formatted_date = self.format_date(date_string)
                    
                    
                self.shared_post_urls.append(shared_post_url)
                self.shared_user_ids.append(shared_user_id)
                self.shared_usernames.append(shared_username)
                self.shared_texts.append(shared_text)
                self.shared_dates.append(shared_formatted_date)
                
            
            else:
                self.shared_user_ids.append('')
                self.shared_usernames.append('')
                self.shared_texts.append('')
                self.shared_dates.append('')
                self.shared_post_urls.append('')
                
            
            #@ IMAGE
            images = self.get_images(r)       
            self.images.append(images)
            
            
        df = pd.DataFrame({
                'post_url': self.post_urls,
                'user_id': self.user_ids,
                'username': self.usernames,
                'post_text': self.post_texts,
                'time': self.dates,
                'shared_post_url': self.shared_post_urls,
                'shared_user_id': self.shared_user_ids,
                'shared_username': self.shared_usernames,
                'shared_text': self.shared_texts,
                'shared_time': self.shared_dates,
                'images': self.images
                
                            })
        
        return df
    
