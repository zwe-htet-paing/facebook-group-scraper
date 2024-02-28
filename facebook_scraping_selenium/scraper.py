# selenium-related
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException


# other necessary ones
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

import utils.tag_config as tag

class FacebookScraper:
    def __init__(self, credentials='credentials.txt', driver_location="../chromedriver-linux64/chromedriver", use_cookies=False, raw_data_dir="data/raw"):
        #@ set options
        self.chrome_option = Options()
        self.chrome_option.add_argument("--headless")  # Run Chrome in headless mode
        self.chrome_option.add_argument("start-maximized")
        self.chrome_option.add_argument("--disable-notifications")
        self.chrome_option.add_argument("--disable-infobars")
        self.chrome_option.add_argument("--disable-extensions")
        self.chrome_option.add_argument("--disable-gpu")  # Disable GPU acceleration
        self.chrome_option.add_argument('--no-sandbox')
        self.chrome_option.add_argument('--disable-dev-shm-usage')
        
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
        
        # start login
        self.login(credentials=credentials, driver_location=driver_location, cookies=use_cookies)

        self.raw_data_dir = raw_data_dir
    
    @staticmethod
    def openSeeMore(browser):
        xpath_exp = "//div[contains(@class,'{}') and contains(text(), 'See more')]"
        try:
            readMore = browser.find_elements(By.XPATH, xpath_exp.format(tag.see_more_tag))
        except:
            pass
        
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
                    
            # if len(readMore) - count > 0:
            #     print('[ERROR]readMore issue:', len(readMore) - count)
            time.sleep(1)
        else:
            pass
        
    @staticmethod 
    def date_handover(browser):
        xpath_exp = "//a[@class='{}']"
        try:
            date_elements = browser.find_elements(By.XPATH, xpath_exp.format(tag.date_tag))
        except:
            pass
        
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
                    
            # if len(date_elements) - count > 0:
            #     print('[ERROR] date_element issue:', len(date_elements) - count)
            time.sleep(1)
        else:
            pass
    
    @staticmethod
    def getBack(browser, end_url):
        if not browser.current_url.endswith(end_url):
            # print('[INFO] redirected!!!')
            browser.back()
            # print('[INFO] got back!!!')
    
    @staticmethod
    def archiveAtEnd(browser, reviewList, group_id, source_data, raw_data_dir, logger):
        # browser.execute_script("window.scrollTo(0, -document.body.scrollHeight);") # scroll back to the top
        # time.sleep(10)
            
        # for idx, l in enumerate(reviewList):
        #     if idx % 10 == 0:
        #         if idx < 15:
        #             browser.execute_script("arguments[0].scrollIntoView();", reviewList[0])
        #         else:
        #             browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx-15])
                
        #         time.sleep(1)
        #         try:
        #             browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+15])
        #         except:
        #             browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])

        #         time.sleep(1)
        #         browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx])
                
        #         for r in range(2):
        #             time.sleep(2)
        #             try:
        #                 browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+5])
        #                 time.sleep(2)
        #             except:
        #                 browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])
        #             browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+r*3])
        #             time.sleep(3)

        # source_data = browser.page_source
        file_path = f'{raw_data_dir}/{group_id}.html'
        with open(file_path, "w", encoding="utf-8") as file:
            bs_data = bs(source_data, 'html.parser')
            file.write(str(bs_data.prettify()))
            logger.info(f'Saving raw data: {group_id}')
                    
        return file_path
    
    @staticmethod
    def save_cookies(browser, filename, logger):
        pickle.dump(browser.get_cookies(), open(filename, 'wb'))
        logger.info("Cookies saved successfully")

    def add_cookies(self, filename):
        cookies = pickle.load(open(filename, 'rb'))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        self.logger.info("Cookies added successfully")

    def check_login(self):
        # Locate the div using its aria-label and class attributes
        div_locator = (By.XPATH, '//div[@aria-label="Create a post" and @class="{}"]'.format(tag.create_post_tag))

        # Wait for the element to be present (adjust the timeout as needed)
        try:
            element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(div_locator))
        except:
            self.logger.error("Login unsuccessful...")
            sys.exit(0)

        self.logger.info("Login successful")

    def login(self, credentials, driver_location, cookies=True):

        if cookies:
            self.logger.info("Starting browser using cookies...")
            self.browser = webdriver.Chrome(service=Service(driver_location), options=self.chrome_option)
            # Delete a cookie with name 'test1'
            self.browser.delete_all_cookies()
            self.browser.get("http://facebook.com")
            self.add_cookies('user_cookies.pkl')
            self.browser.refresh() #refresh the page
            self.check_login()
        else:
            #@ credentials
            with open(credentials) as file:
                self.EMAIL = file.readline().split('"')[1]
                self.PASSWORD = file.readline().split('"')[1]
            
            self.logger.info("Starting browser...")
            self.browser = webdriver.Chrome(service=Service(driver_location), options=self.chrome_option)
            self.browser.get("http://facebook.com")
            self.browser.maximize_window()
            wait = WebDriverWait(self.browser, 30)

            self.logger.info("Logging in...")
            email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
            email_field.send_keys(self.EMAIL)
            pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
            pass_field.send_keys(self.PASSWORD)
            pass_field.send_keys(Keys.RETURN)
            
            # time.sleep(3)
            # Wait for the login process to complete
            wait.until(EC.url_contains("facebook.com"))
            self.check_login()
            self.save_cookies(self.browser, 'user_cookies.pkl', self.logger)
        
    def close(self):
        self.logger.info("Closing browser")
        self.browser.close()
    
    def get_source(self, target_id, num_posts=100):
        
        # once logged in, free to open up any target page
        self.logger.info("*" * 40)
        self.logger.info(f"Getting source ...")
        self.logger.info(f"Go to target URL: {target_id}...")
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
            postsList = None
            last_post = None
            
            self.date_handover(self.browser)
            self.openSeeMore(self.browser)
            self.getBack(self.browser, end_url)

            # # scroll to the bottom
            # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(3)

            # # process check
            # # get content
            # postsList = browser.find_elements(By.XPATH, "//div[@class='{}']".format(tag.post_list_tag))
            # numPosts = len(postsList)
            # if old_numPosts < numPosts:
            #     self.logger.info(f'Scroll Count: {count}  numPosts: { numPosts}')
            # old_numPosts = numPosts
            
            # Get the last post element
            time.sleep(2)
            postsList = self.browser.find_elements(By.XPATH, "//div[@class='{}']".format(tag.post_list_tag))
            # if postsList:
            #     last_post = postsList[-1]
            #     self.browser.execute_script("arguments[0].scrollIntoView();", last_post)
            #     time.sleep(2)

            if postsList:
                last_post = postsList[-1]
                # Scroll to the last post element
                try:
                    # Using WebDriverWait to wait until the element is clickable
                    wait = WebDriverWait(self.browser, 10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='{}']".format(tag.post_list_tag))))
                    self.browser.execute_script("arguments[0].scrollIntoView();", last_post)
                    time.sleep(2)   
                except StaleElementReferenceException:
                    # Handle StaleElementReferenceException by re-finding the last post element
                    print("StaleElementReferenceException. Retrying...")
                    postsList = self.browser.find_elements(By.XPATH, "//div[@class='{}']".format()(tag.post_list_tag))
                    if postsList:
                        last_post = postsList[-1]
                        self.browser.execute_script("arguments[0].scrollIntoView();", last_post)
                        time.sleep(2)
            else:
                self.logger.info("No posts found.")

            # process check
            numPosts = len(postsList)
            self.logger.info(f'Scroll Count: {count}  numPosts: { numPosts}')

            if numPosts > old_numPosts:
                old_numPosts = numPosts
                page_source = self.browser.page_source
            else:
                self.logger.info(f"Error Scrolling...")
                # return page_source
                file_path = self.archiveAtEnd(self.browser, postsList, target_id, source_data=page_source, raw_data_dir=self.raw_data_dir, logger=self.logger)
                return file_path


            # termination condition
            if (numPosts >= specifiedNumber):
                switch = False
                self.date_handover(self.browser)
                self.openSeeMore(self.browser)
                self.getBack(self.browser, end_url)
                    
        # Get the page source after all content is loaded
        page_source = self.browser.page_source
        file_path = self.archiveAtEnd(self.browser, postsList, target_id, source_data=page_source, raw_data_dir=self.raw_data_dir, logger=self.logger)

        return file_path   
            
    # def scrape_group(self, group_id, num_posts=10):
    #     page_source = self.get_source(group_id, num_posts=num_posts) 
    #     self.close()
    #     df = self.extract_data(group_id=group_id)
    #     self.logger.info(f"Done")
    #     self.write_csv(df, f"group_{group_id}_{len(df)}.csv")
    #     return df
        
    # def scrape_groups(self, group_ids:list, num_posts=10):
    #     for group_id in group_ids:
    #         page_source = self.get_source(group_id, num_posts=num_posts) 
    #         df = self.extract_data(page_source)
    #         self.logger.info(f"Done, write to csv {group_id}")
    #         self.write_csv(df, f"group_{group_id}_{len(df)}.csv")
            
    #     self.close()
    