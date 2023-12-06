import pytest
from bs4 import BeautifulSoup as bs
from facebook_scraping_selenium.scraper import FacebookScraper

page_id = 'eieiwin155'
group_id = '1605099990009060'

credentials = "credentials.txt"
driver_location = "../chromedriver-linux64/chromedriver"
fb_scraper = FacebookScraper(credentials, driver_location)

page_source = fb_scraper.get_source(group_id, num_posts=5)

page = bs(page_source, 'lxml')
group_posts = page.find_all('div', {'class': 'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z'})

def test_valid_page_source_tag():
    assert page_source is not None

def test_valid_content_tag():
    assert group_posts is not None

def test_valid_post_url():
    for post in group_posts[1:]:
        post_id = fb_scraper.get_post_url(post)
        assert post_id is not None

def test_valid_user_info():
    for post in group_posts[1:]:
        user, username = fb_scraper.get_user(post)
        assert user is not None
        assert username is not None

def test_valid_text():
    for post in group_posts[1:]:
        text = fb_scraper.get_text(post)
        assert text is not None

def test_valid_date_string():
    for post in group_posts[1:]:
        date_string = fb_scraper.get_date_string(post, page)
        assert date_string is not None