# selenium-related
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

# other necessary ones
import urllib.request
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import time
import re
import datetime
import logging

from custom_utils import parse_datetime

class FacebookScraper:
    def __init__(self, credentials):
        #@ set options
        self.chrome_option = Options()
        self.chrome_option.add_argument("--headless")  # Run Chrome in headless mode 
        self.chrome_option.add_argument("--disable-notifications")
        self.chrome_option.add_argument("--disable-infobars")
        self.chrome_option.add_argument("--disable-extensions")
        self.chrome_option.add_argument("start-maximized")
        
        # self.chrome_option.add_argument("--disable-gpu")  # Disable GPU acceleration
        # self.chrome_option.add_argument('--no-sandbox')
        # self.chrome_option.add_argument('--disable-dev-shm-usage')
        
        #@ custom logger
        self.logger = logging.getLogger("FacebookScraper")
        self.logger.setLevel(logging.INFO)
        
        # Create a console handler and set its level to INFO
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        # Create a formatter and set the formatter for the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
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
        self.shared_images = []
        
        # start login
        self.login(credentials=credentials)
    
    @staticmethod
    def openSeeMore(browser):
        
        see_more_tag = 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f'
        xpath_exp = "//div[contains(@class,'{}') and contains(text(), 'See more')]"
        readMore = browser.find_elements(By.XPATH, xpath_exp.format(see_more_tag))
        
        if len(readMore) > 0:    
            count = 0
            for i in readMore:
                action=ActionChains(browser)
                try:
                    action.move_to_element(i).click().perform()
                    time.sleep(1)
                    count += 1
                except:
                    try:
                        browser.execute_script("arguments[0].click();", i)
                        time.sleep(1)
                        count += 1
                    except:
                        continue
                    
            if len(readMore) - count > 0:
                print('readMore issue:', len(readMore) - count)
            time.sleep(1)
        else:
            pass
        
    @staticmethod 
    def date_handover(browser):

        date_tag = 'x1rg5ohu x6ikm8r x10wlt62 x16dsc37 xt0b8zv'
        xpath_exp = "//span[@class='{}']"
        date_elements = browser.find_elements(By.XPATH, xpath_exp.format(date_tag))
        # date_elements = WebDriverWait(browser, 30).until(EC.presence_of_all_elements_located((By.XPATH, xpath_exp.format(date_tag))))

        # wait = WebDriverWait(browser, 30)
        # element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm']")))
        if len(date_elements) > 0:
            count = 0
            for i in date_elements:
                action=ActionChains(browser)
                try:
                    action.move_to_element(i).perform()
                    time.sleep(1)
                    # print(element.get_attribute("href"))
                    # wait.until(lambda browser: element.get_attribute("href") != "#")
                    count += 1
                    
                except:
                    try:
                        # print("java script scroll")
                        browser.execute_script("arguments[0].scrollIntoView();", i)
                        # time.sleep(1)
                        # print(element.get_attribute("href"))
                        count += 1
                    except:
                        continue
                    
            if len(date_elements) - count > 0:
                print('date_element issue:', len(date_elements) - count)
            time.sleep(1)
        else:
            pass
    
    @staticmethod
    def getBack(browser, end_url):
        if not browser.current_url.endswith(end_url):
            print('redirected!!!')
            browser.back()
            print('got back!!!')
    
    @staticmethod
    def archiveAtEnd(browser, reviewList):
        browser.execute_script("window.scrollTo(0, -document.body.scrollHeight);") # scroll back to the top
        time.sleep(10)
            
        for idx, l in enumerate(reviewList):
            if idx % 10 == 0:
                if idx < 15:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[0])
                else:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx-15])
                
                time.sleep(1)
                try:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+15])
                except:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])

                time.sleep(1)
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx])
                
                for r in range(2):
                    time.sleep(2)
                    try:
                        browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+5])
                        time.sleep(2)
                    except:
                        browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+r*3])
                    time.sleep(3)
                    
                # with open(f'{PATH}/{str(idx)}_{r}.html',"w", encoding="utf-8") as file:
                #     source_data = browser.page_source
                #     bs_data = bs(source_data, 'html.parser')
                #     file.write(str(bs_data.prettify()))
                #     print(f'written: {idx}_{r}')
                    
        source_data = browser.page_source
        
        return source_data
    
    @staticmethod
    def format_date(date_string):
        # today_date = datetime.datetime.now()
        # date_parts = date_string.split()
        
        # if 'seconds' in date_parts:
        #     formatted_date = today_date
        # elif 'minute' in date_parts:
        #     minutes_ago = 1
        #     formatted_date = today_date - datetime.timedelta(minutes=minutes_ago)
        # elif 'minutes' in date_parts:
        #     minutes_ago = int(date_parts[0])
        #     formatted_date = today_date - datetime.timedelta(minutes=minutes_ago)    
        # elif 'hour' in date_parts:
        #     hours_ago = 1
        #     formatted_date = today_date - datetime.timedelta(hours=hours_ago)
        # elif 'hours' in date_parts:
        #     hours_ago = int(date_parts[0])
        #     formatted_date = today_date - datetime.timedelta(hours=hours_ago)
        # elif 'day' in date_parts:
        #     days_ago = 1
        #     formatted_date = today_date - datetime.timedelta(days=days_ago)
        # elif 'days' in date_parts:
        #     days_ago = int(date_parts[0])
        #     formatted_date = today_date - datetime.timedelta(days=days_ago)
        # else:
        #     formatted_date = today_date
        
        # # Format the date without seconds
        # formatted_date = formatted_date.strftime('%Y-%m-%d %H:%M')
        
        formatted_date = parse_datetime(date_string)
        
        return formatted_date
    
    def login(self, credentials):
        #@ credentials
        with open(credentials) as file:
            self.EMAIL = file.readline().split('"')[1]
            self.PASSWORD = file.readline().split('"')[1]
            
        self.logger.info("Starting browser...")
        self.browser = webdriver.Chrome(service=Service("../chromedriver-linux64/chromedriver"), options=self.chrome_option)
        self.browser.get("http://facebook.com")
        self.browser.maximize_window()
        wait = WebDriverWait(self.browser, 30)

        self.logger.info("Logging in...")
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
        email_field.send_keys(self.EMAIL)
        pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
        pass_field.send_keys(self.PASSWORD)
        pass_field.send_keys(Keys.RETURN)

        time.sleep(3)
        
    def close(self):
        self.logger.info("Closing browser")
        self.browser.close()
    
    def get_source(self, target_id, credentials, num_posts=20):
        
        # once logged in, free to open up any target page
        self.logger.info(f"Getting source to {target_id} ...")
        self.logger.info("Go to target URL...")
        self.browser.get(f"https://wwww.facebook.com/{target_id}")

        time.sleep(3)
        url = self.browser.current_url
        if 'groups' in url.split('/'):
            end_url = url.split('groups/')[-1]
            # self.logger.info(end_url)
        else:
            end_url = target_id

        count = 0
        switch = True
        old_numPosts = 0
        specifiedNumber = num_posts # number of posts to get

        while switch:
            count += 1
            
            self.date_handover(self.browser)
            self.openSeeMore(self.browser)
            self.getBack(self.browser, end_url)

            # # scroll to the bottom
            # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(3)

            # # process check
            # # get content
            # postsList = browser.find_elements(By.XPATH, "//div[@class='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z']")
            # numPosts = len(postsList)
            # if old_numPosts < numPosts:
            #     self.logger.info(f'Scroll Count: {count}  numPosts: { numPosts}')
            # old_numPosts = numPosts

            # # termination condition
            # if numPosts >= specifiedNumber:
            #     switch = False
            
            # Get the last post element
            postsList = self.browser.find_elements(By.XPATH, "//div[@class='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z']")
            if postsList:
                last_post = postsList[-1]

            # Scroll to the last post element
            if last_post:
                self.browser.execute_script("arguments[0].scrollIntoView();", last_post)
                time.sleep(2)

            # process check
            numPosts = len(postsList)
            self.logger.info(f'Scroll Count: {count}  numPosts: { numPosts}')

            # termination condition
            if numPosts >= specifiedNumber:
                switch = False
                
                self.date_handover(self.browser)
                self.openSeeMore(self.browser)
                self.getBack(self.browser, end_url)
                
                
        # Get the page source after all content is loaded
        page_source = self.browser.page_source
        # page_source = self.archiveAtEnd(browser, postsList)
        
        return page_source
    
    @staticmethod
    def get_post_url(r):    
        posts_tag = 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm'
        post_id = r.find('a', {'class':posts_tag}).get('href')
        
        return post_id
    
    @staticmethod
    def get_user(r):    
        user_tag = 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f'
        user_element = r.find('a',{'class':user_tag})
        
        #@ username
        if user_element is not None:
            username = user_element.get_text().strip()
            
            #@ user_id
            user_id = user_element.get('href')[25:].split('?')[0]
            if user_id == 'profile.php':
                user_id = user_element.get('href').split('?id=')[1].split('&')[0]
            
        else:
            #@ anonymous user
            user_element = r.find('div', {'class':user_tag})
            username = user_element.get_text().strip()
            user_id = 'None'
            
            
        return user_id, username
    
    @staticmethod
    def get_text(r):
        text_tag = 'x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h'
        text_element = r.find('span',{'class':text_tag})
        if text_element is not None:
            text = text_element.get_text().strip()
        else:
            text_element = r.find('div',{'class':'x1iorvi4 x1pi30zi x1l90r2v x1swvt13'})
            if text_element is not None:
                text = text_element.get_text().strip()
            else:
                text_element = r.find('div', {'class':'x6s0dn4 x78zum5 xdt5ytf x5yr21d xl56j7k x10l6tqk x17qophe x13vifvy xh8yej3'})
                if text_element is not None:
                    text = text_element.get_text().strip()
                else:
                    text = 'no_text'
        
        return text
    
    @staticmethod
    def get_date_index(r):          
        span_element = r.find('span', {'class':'x1rg5ohu x6ikm8r x10wlt62 x16dsc37 xt0b8zv'})
        
        if span_element is not None:
            # date_index = span_element['aria-labelledby']
            date_index = span_element.find('use')['xlink:href'][1:]
            return date_index
        
        else:
            return None
    
    @staticmethod
    def write_csv(df, filename):
        df.to_csv(filename)
    
    # def get_images(self, r):
    #     #@ images
    #     image_tag='xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3'
    #     image_element=r.find_all('img', {'class':image_tag})

    #     if image_element is not None:
    #         temp_images = []
    #         for image in image_element:
    #             temp_images.append(image['src'])
                
    #         self.images.append(temp_images)
    #     else:
    #         self.images.append(None)
    
    def extract_data(self, page_source):    
        page = bs(page_source, 'lxml')
        group_posts = page.find_all('div', {
            'class':'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z'
                                    })
        
        for idx, r in enumerate(group_posts[1:]):
            
            # if idx == 20:
            #     break
            
            #@ post_url
            post_url = self.get_post_url(r)
            self.post_urls.append(post_url)

            #@ user_id and username
            user_id, username = self.get_user(r)
            self.user_ids.append(user_id)
            self.usernames.append(username)
            
            #@ text
            text = self.get_text(r)
            self.post_texts.append(text)
            
            #@ date
            date_index = self.get_date_index(r)  
            
            # date_element = page.find('span', {'id':str(date_index)})
            date_element = page.find('text', {'id':str(date_index)})
            if date_element is not None:
                date = date_element.text.strip()
                formated_date = self.format_date(date)
            else:
                # formated_date = 'None'
                date_tag = "x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"
                date = r.find('span', {'class':date_tag}).get_text()
                formated_date = self.format_date(date)
            self.dates.append(formated_date)
            
            
            #@ shared post
            share_post_tag = 'x1jx94hy x8cjs6t x1ch86jh x80vd3b xckqwgs x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x178xt8z xm81vs4 xso031l xy80clv xfh8nwu xoqspk4 x12v9rci x138vmkv x6ikm8r x10wlt62 x16n37ib xq8finb'     
            shared_post = r.find('div', {'class':share_post_tag})
            
            if shared_post is not None:
                
                #@ shared post_url
                shared_post_url = self.get_post_url(shared_post)
            
                #@ shared user id and username
                shared_user_id, shared_username = self.get_user(shared_post)         
                
                #@ shared text
                shared_text_element = shared_post.find('div',{'class':'x1iorvi4 x1pi30zi x1l90r2v x1swvt13'})
                if shared_text_element is not None:
                    shared_text = shared_text_element.get_text().strip()
                else:
                    shared_text = 'no text'
                
                # #@ shared date 
                date_index = self.get_date_index(shared_post)
                
                # shared_date_element = page.find('span', {'id':str(date_index)})
                shared_date_element = page.find('text', {'id':str(date_index)})
                if shared_date_element is not None:
                    shared_date = date_element.text.strip()
                    # self.logger.info("shared_date: ", shared_date.strip())
                    shared_formated_date = self.format_date(shared_date)
                else:
                    shared_formated_date = 'None' 
                    
                    
                self.shared_post_urls.append(shared_post_url)
                self.shared_user_ids.append(shared_user_id)
                self.shared_usernames.append(shared_username)
                self.shared_texts.append(shared_text)
                self.shared_dates.append(shared_formated_date)
                
            
            else:
                self.shared_user_ids.append('None')
                self.shared_usernames.append('None')
                self.shared_texts.append('None')
                self.shared_dates.append('None')
                self.shared_post_urls.append('None')
                
            
            #@ images
            image_tag='xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3'
            image_element=r.find_all('img', {'class':image_tag})
            
            image_tag1='x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3 xl1xv1r'
            image_element1=r.find_all('img', {'class':image_tag1})
            

            temp_images = []
            if image_element is not None:
                for image in image_element:
                    temp_images.append(image['src'])
                    
            if image_element1 is not None:
                for image in image_element1:
                    temp_images.append(image['src'])
                    
            self.images.append(temp_images)
            
            
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
            
    def scrape_group(self, group_id):
        page_source = self.get_source(group_id, credentials='credentials.txt', num_posts=10) 
        self.close()
        df = self.extract_data(page_source)
        self.write_csv(df, f"test_{group_id}.csv")
        
    def scrape_groups(self, group_ids:list):
        for group_id in group_ids:
            page_source = self.get_source(group_id, credentials='credentials.txt', num_posts=10) 
            df = self.extract_data(page_source)
            self.logger.info(f"Done, write to csv {group_id}")
            self.write_csv(df, f"test_{group_id}.csv")
            
        self.close()
    