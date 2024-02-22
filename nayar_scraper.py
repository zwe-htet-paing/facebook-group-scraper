import os
import time
import logging
from pathlib import Path
import glob
import argparse
from datetime import datetime

import re
import pandas as pd
from facebook_scraping_selenium.scraper import FacebookScraper
from facebook_scraping_selenium.extractor import Extractor


def get_group_dict(filepath: str):
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
        # group_id = matches.group(1)
        post_id = matches.group(2)
        # print("Group ID:", group_id)
        # print("Post ID:", post_id)
        return post_id
    else:
        # print("URL format doesn't match the expected pattern.")
        return None


def preprocess_df(df: pd.DataFrame, date_list: list, filter_date=True):
    # Remove invalid links
    df = df[(df['post_url'] != '#') & (df['shared_post_url'] != '#')
            & (df['time'] is not None) & (df['post_url'].notna())]
    df_clean = df.copy()
    
    # Convert the 'time' to datetime format
    df_clean['time'] = pd.to_datetime(df_clean['time'])
    
    if filter_date:
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
    # custom logger
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


def run(
        group_file_path="/data/nayar_public_active_groups.csv",
        output_path="/data/downloads",
        resume=False,
        posts_lookup=10,
        date_string="2024-02-07",
        extra_date=None,
        use_cookie=True,
        credentials='credentials.txt',
        driver_location='local'  # docker
):
    start_program = time.time()
    logger = get_logger()
    
    if driver_location == "docker":
        driver_location = '/usr/bin/chromedriver'
        root_dir = '/app'
    else:
        driver_location = "../chromedriver-linux64/chromedriver"
        root_dir = '.'

    # handle resume or not
    os.makedirs(f"{root_dir}/data/checkpoint", exist_ok=True)
    if resume == False and os.path.exists(f"{root_dir}/data/checkpoint/done.txt"):
        os.remove(f"{root_dir}/data/checkpoint/done.txt")
    
    # Keep list of already done targets
    if Path(f'{root_dir}/data/checkpoint/done.txt').exists():
        with open(f'{root_dir}/data/checkpoint/done.txt', 'r') as f:
            done = f.read().splitlines()
    else:
        done = list()
    
    # Take care of download path
    if date_string is None:
        current_time = datetime.now()
        date_string = current_time.strftime("%Y-%m-%d")
        filter_date = False
    else:
        filter_date = True

    # raw data folder
    os.makedirs(f'{root_dir}/data/raw', exist_ok=True)
    raw_data_dir = f"{root_dir}/data/raw/{date_string}"
    os.makedirs(raw_data_dir, exist_ok=True)
        
    folder_path = Path(os.path.join(root_dir+output_path, date_string))
    # folder_path.mkdir(exist_ok=True)
    os.makedirs(folder_path, exist_ok=True)
    
    # Take care of date list
    date_list = []
    date_list.append(date_string)
    
    # include extra date
    if extra_date is not None:
        extra_date_list = extra_date.split(',')
    else:
        extra_date_list = []
    date_list += extra_date_list
    logger.info(f"Date: {date_list}")

    # Get group dict
    group_dict = get_group_dict(root_dir+group_file_path)

    # Initialize FacebokScraper
    fb_scraper = FacebookScraper(credentials, driver_location, use_cookies=use_cookie, raw_data_dir=raw_data_dir)
    extractor = Extractor()
    # Main loop
    for idx, group_id in enumerate(list(group_dict.keys())):  # [:10] limit to 10 groups
        logger.info(f"{'*' * 40}")
        if str(group_id) in done:
            logger.info(f"Group ID {idx+1}: {group_id} already done... ")
            continue
        else:
            logger.info(f"{'*'*6} Group ID {idx+1}: {group_id} {'*'*6}")
        start_time = time.time()
        # Get target page_source
        file_path = fb_scraper.get_source(group_id, num_posts=posts_lookup)
        # Extract data from page_source
        try:
            logger.info("Started extracting data")
            df = extractor.extract_data(source_file=file_path)
            # Preprocess data
            df = preprocess_df(df, date_list, filter_date)
            
            # check dataframe length
            if len(df) == 0:
                logger.info("No data for provided date...")
            else:
                # Write data to csv 
                extractor.write_csv(df, f"{folder_path}/group_{group_id}_{len(df)}.csv")
        except:
            pass
        
        #@ add group to dont.txt    
        done.append(group_id)
        with open(f"{root_dir}/data/checkpoint/done.txt", 'a') as f:
            f.write(str(group_id))
            f.write('\n')
        
        logger.info(f"Group ID: {group_id} complete.") # Get {len(df)} posts.
        end_time = time.time()
        
        # Calculate elapsed time in minutes
        elapsed_time = (end_time - start_time) / 60
        logger.info(f"Elapsed Time: {elapsed_time:.2f} minutes")

    # close browser
    fb_scraper.close()

    # get all group csv file and combine dataframe
    logger.info(f"{'*' * 40}")
    logger.info(f"Getting all data for date: {date_string}...")
    final_df = get_data_for_one_date(date_string=date_string, data_path=root_dir+output_path)
    
    # Save the DataFrame to a CSV file in the specified folder
    output_folder = os.path.join(root_dir+output_path, 'output')
    os.makedirs(output_folder, exist_ok=True)

    output_file_path = os.path.join(output_folder, f"{date_string}_output_{len(final_df)}.csv")
    final_df.to_csv(output_file_path, index=False)
    logger.info(f"DataFrame saved to {output_file_path}")
    
    end_program = time.time()    
    # Calculate elapsed time in minutes
    elapsed_time = (end_program - start_program) / 60
    logger.info(f"Elapsed Time: {elapsed_time:.2f} minutes")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--group_file_path", type=str, default="/data/nayar_public_active_groups.csv", help='Path of group csv file.')
    parser.add_argument("--output_path", type=str, default="/data/downloads", help='Path of output folder.')
    parser.add_argument("--resume", action='store_true', default=False, help="Enable resume mode.")
    parser.add_argument("--use_cookies", action="store_true", default=False, help="Enable cookies usage.")
    parser.add_argument("--date", type=str, default=None, help="Date in format YYYY-MM-DD.")
    parser.add_argument("--extra_date", type=str, default=None, help="Extra date in format YYYY-MM-DD if needed. Use comma if multiple date.")
    parser.add_argument("--posts_lookup", type=int, default=200, help="Number of posts to check.")
    parser.add_argument("--credentials", type=str, default="credentials.txt", help="Path of credentials file in .txt format.")
    parser.add_argument("--driver_location", type=str, default="local", help="Path of chrome driver location egs. docker, local.")

    # run()
    args = parser.parse_args()
    # print(args.resume)
    # print(args.extra_date.split(','))

    run(
        date_string=args.date,
        extra_date=args.extra_date,
        posts_lookup=args.posts_lookup,
        group_file_path=args.group_file_path,
        output_path=args.output_path,
        resume=args.resume,
        use_cookie=args.use_cookies,
        credentials=args.credentials,
        driver_location=args.driver_location
    )
    