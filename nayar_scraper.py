import os
import time
import logging
from pathlib import Path
import glob
from datetime import datetime

import re
import pandas as pd
from facebook_scraping_selenium.scraper import FacebookScraper

def get_group_dict(filepath:str):
    """
    Read data from csv file, preprocess and return group dict.
    """
    
    nayar_group = pd.read_csv(filepath)

    group_dict = nayar_group.set_index('id')['name'].to_dict()
    
    return group_dict


def extract_post_id(url):
    # Regular expression pattern to extract group_id and post_id
    pattern = r'groups/(\d+)/posts/(\d+)/'

    # Extracting group_id and post_id using regular expression
    matches = re.search(pattern, url)

    if matches:
        group_id = matches.group(1)
        post_id = matches.group(2)
        # print("Group ID:", group_id)
        # print("Post ID:", post_id)
        return post_id
    else:
        # print("URL format doesn't match the expected pattern.")
        return None


def preprocess_df(df:pd.DataFrame, date_list:list):
    # Remove invalid links
    df = df[(df['post_url'] != '#') & (df['shared_post_url'] != '#') & (df['time'] != None)]
    df_clean = df.copy()
    
    # Convert the 'time' to datetime format
    df_clean['time'] = pd.to_datetime(df_clean['time'])
    
    # Filter rows where 'time' is in provided dates
    df_clean = df_clean[df_clean['time'].dt.date.astype(str).isin(date_list)]
    
    # Check if post_text and shared_user_name are the same, then replace post_text with an empty string
    mask = df_clean['post_text'] == df_clean['shared_username']
    df_clean.loc[mask, 'post_text'] = ''
    
    # Check if post_text and username are the same, then replace post_text with an empty string
    mask = df_clean['post_text'] == df_clean['username']
    df_clean.loc[mask, 'post_text'] = ''
    
    # Concatenate 'post_text' and 'shared_text' handling NaN values
    text = (df_clean['post_text'].fillna('') + df_clean['shared_text'].fillna(''))
    df_clean.loc[:, 'text'] = text
    
    # Drop duplicate
    df_clean = df_clean.drop_duplicates(subset=['text'], keep='first')
    
    # Reset index
    df_clean.reset_index(drop=True, inplace=True)
    
    # Get post_id from post_url
    df_clean["post_id"] = df_clean["post_url"].apply(extract_post_id)
    
    return df_clean


def get_data_for_one_date(date_string: str, data_path: str):
    # Convert date string to datetime.date object
    # date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
    # print("[INFO] DATE: ", date_string)
    
    folder_path = os.path.join(data_path, date_string)
    file_list = glob.glob(os.path.join(folder_path, '*.csv'))
    
    final_df = pd.DataFrame()
    
    for file in file_list:
        # print(file)
        group_id = file.split('_')[1]
        
        temp_df = pd.read_csv(file)
        
        # Add 'group_id' column
        temp_df['group_id'] = group_id
        
        # Concatenate to the final DataFrame
        final_df = pd.concat([final_df, temp_df], ignore_index=True)
    
    # Drop duplicates based on 'text' column
    final_df.drop_duplicates(subset=['text'], inplace=True)
    
    # Reset index
    final_df.reset_index(drop=True, inplace=True)
    
    return final_df


def get_logger(name="nayar_scraper"):
    #@ custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create a console handler and set its level to INFO
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    # Create a formatter and set the formatter for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
    
if __name__ == "__main__":
    start_program = time.time()
    logger = get_logger()
    group_file_path = "./data/nayar_public_active_groups.csv"
    output_path="./data/downloads"
    
    #########################
    resume = False
    posts_lookup = 150
    #########################
    
    # handle resume or not
    if resume == False and os.path.exists("./data/done.txt"):
        os.remove("./data/done.txt")
    
    # Keep list of already done targets
    if Path('./data/done.txt').exists():
        with open('./data/done.txt', 'r') as f:
            done = f.read().splitlines()
    else:
        done = list()
    
    # Take care of download path
    # current_time = datetime.now()
    # date_string = current_time.strftime("%Y-%m-%d")
    ##############################
    date_string = "2024-02-01"
    ##############################
    folder_path = Path(os.path.join(output_path, date_string))
    folder_path.mkdir(exist_ok=True)
    
    # Take care of date list
    date_list = []
    date_list.append(date_string)
    
    ##############################
    extra_date_list = None
    ##############################
    if extra_date_list is not None:
        date_list += extra_date_list
    
    # Get group dict
    group_dict = get_group_dict(group_file_path)
    # print(group_dict)
    
    # Initialize FacebokScraper
    #######################
    has_cookie = True
    #######################
    credentials = 'credentials.txt'
    driver_location="../chromedriver-linux64/chromedriver"
    fb_scraper = FacebookScraper(credentials, driver_location, use_cookies=has_cookie)
    
    # Main loop
    for idx, group_id in enumerate(list(group_dict.keys())): # [:10] limit to 10 groups
        logger.info(f"{'*' * 40}")
        if str(group_id) in done:
            logger.info(f"Group ID {idx+1}: {group_id} already done... ")
            continue
        else:
            logger.info(f"{'*'*6} Group ID {idx+1}: {group_id} {'*'*6}")
        start_time = time.time()
        # Get target page_source
        page_source = fb_scraper.get_source(group_id, num_posts=posts_lookup)
        # Extract data from page_source
        df = fb_scraper.extract_data(page_source)
        # Preprocess data
        df = preprocess_df(df, date_list)
        
        # check dataframe length
        if len(df) == 0:
            logger.info("No data for provided date...")
        else:
            # Write data to csv 
            fb_scraper.write_csv(df, f"{folder_path}/group_{group_id}_{len(df)}.csv")
        
        #@ add group to dont.txt    
        done.append(group_id)
        with open(f"./data/done.txt", 'a') as f:
            f.write(str(group_id))
            f.write('\n')
            
        logger.info(f"Group ID: {group_id} complete...")
        end_time = time.time()
        
        # Calculate elapsed time in minutes
        elapsed_time = (end_time - start_time) / 60
        logger.info(f"Elapsed Time: {elapsed_time:.2f} minutes")

    # close browser
    fb_scraper.close()
    
    # get all group csv file and combine dataframe
    logger.info(f"{'*' * 40}")
    logger.info(f"Getting all data for date: {date_string}...")
    final_df = get_data_for_one_date(date_string=date_string, data_path=output_path)
    
    # Save the DataFrame to a CSV file in the specified folder
    output_folder = os.path.join(output_path, 'output')
    os.makedirs(output_folder, exist_ok=True)

    output_file_path = os.path.join(output_folder, f"{date_string}_output_{len(final_df)}.csv")
    final_df.to_csv(output_file_path, index=False)
    logger.info(f"DataFrame saved to {output_file_path}")
    
    end_program = time.time()    
    # Calculate elapsed time in minutes
    elapsed_time = (end_program - start_program) / 60
    logger.info(f"Elapsed Time: {elapsed_time:.2f} minutes")
    