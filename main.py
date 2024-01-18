from facebook_scraping_selenium.scraper import FacebookScraper
import time
import sys

page_id = 'eieiwin155'
group_id = '1605099990009060'
group_ids = ['1605099990009060']

start_time = time.time()

try:
    fb_scraper = FacebookScraper(credentials='credentials.txt')
except Exception as e:
    print(f"An unexpected error occurred during login: {e}")
    sys.exit()  # Exit the script if an exception occurs
else:        
    fb_scraper.scrape_group(group_id)
    # fb_scraper.scrape_groups(group_ids=group_ids)

elasped_time = (time.time() - start_time) / 60
print(f"[INFO] elasped time: {elasped_time} minutes")