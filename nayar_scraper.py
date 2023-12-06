import os
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
        print("URL format doesn't match the expected pattern.")
        return None

def preprocess_df(df:pd.DataFrame):
    # Remove invalid links
    df = df[(df['post_url'] != '#') & (df['shared_post_url'] != '#')]
    df_clean = df.copy()
    
    # Concatenate 'post_text' and 'shared_text' handling NaN values
    text = (df_clean['post_text'].fillna('') + df_clean['shared_text'].fillna(''))
    df_clean.loc[:, 'text'] = text
    
    # Drop duplicate
    df_clean = df_clean.drop_duplicates(subset=['text'], keep='first')
    
    # Reset index
    df_clean.reset_index(drop=True, inplace=True)
    
    df_clean["post_id"] = df_clean["post_url"].apply(extract_post_id)
    
    return df_clean


def get_data_for_one_date(date_string: str, data_path: str):
    # Convert date string to datetime.date object
    # date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
    print("[INFO] DATE: ", date_string)
    
    folder_path = os.path.join(data_path, date_string)
    file_list = glob.glob(os.path.join(folder_path, '*.csv'))
    
    final_df = pd.DataFrame()
    
    for file in file_list:
        print(file)
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


if __name__ == "__main__":
    group_file_path = "./data/nayar_public_active_groups.csv"
    output_path="./data/downloads"
    
    date_string = "2023-12-05"
    folder_path = Path(os.path.join(output_path, date_string))
    folder_path.mkdir(exist_ok=True)
    
    # Get group dict
    group_dict = get_group_dict(group_file_path)
    # print(group_dict)
    
    # Initialize FacebokScraper
    credentials = 'credentials.txt'
    driver_location="../chromedriver-linux64/chromedriver"
    fb_scraper = FacebookScraper(credentials, driver_location)
    
    # Main loop
    for group_id in list(group_dict.keys())[:10]: # limit to 10 groups
        print(f"[INFO] Group ID: {group_id}")
        # Get target page_source
        page_source = fb_scraper.get_source(group_id, num_posts=5)
        # Extract data from page_source
        df = fb_scraper.extract_data(page_source)
        # Preprocess data
        df = preprocess_df(df)
        # Write data to csv 
        fb_scraper.write_csv(df, f"{folder_path}/group_{group_id}_{len(df)}.csv")
    
    # close browser
    fb_scraper.close()
    
    # get all group csv file and combine dataframe
    final_df = get_data_for_one_date(date_string=date_string, data_path=output_path)
    
    # Save the DataFrame to a CSV file in the specified folder
    output_folder = os.path.join(output_path, 'output')
    os.makedirs(output_folder, exist_ok=True)

    output_file_path = os.path.join(output_folder, f"{date_string}_output_{len(final_df)}.csv")
    final_df.to_csv(output_file_path, index=False)
    print(f"[INFO] DataFrame saved to {output_file_path}")