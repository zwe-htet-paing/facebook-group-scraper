from glob import glob
import os
import time
import pandas as pd
from facebook_scraping_selenium.extractor import Extractor
from nayar_scraper import preprocess_df

def get_data_for_one_date(folder_path: str):
    # Convert date string to datetime.date object
    # date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
    # print("[INFO] DATE: ", date_string)
    
    # folder_path = os.path.join(data_path, date_string)
    file_list = glob(os.path.join(folder_path, '*.csv'))
    
    final_df = pd.DataFrame()
    
    for file in file_list:
        group_id = file.split('/')[-1].split('.')[-2].split('_')[-2]

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
    date_string = "2024-02-27"
    output_name =  "scrape_data" # "download" or "scrape_data"
    filter_date = True
    combine_only = False
    folder_path = f"data/raw/{date_string}"
    output_path = f"data/{output_name}/{date_string}"
    os.makedirs(output_path, exist_ok=True)

    extractor = Extractor()

    if combine_only is False:
        for raw_file in glob(os.path.join(folder_path, "*.html")):
            start_time = time.time()
            group_id = raw_file.split("/")[-1].split(".")[0]
            # print(raw_file)
            print(f"[INFO] Group ID: {group_id}")
            temp_df = extractor.extract_data(source_file=raw_file)
            clean_df = preprocess_df(temp_df, date_list=[date_string], filter_date=filter_date)
            extractor.write_csv(clean_df, f"{output_path}/group_{group_id}_{len(clean_df)}.csv")

            end_time = time.time()
            elapsed_time = (end_time - start_time) / 60
            print(f"[INFO] Elapsed Time: {elapsed_time:.2f} minutes")


    print("[INFO] Combining data...")
    final_df = get_data_for_one_date(output_path)

    # final_df['time'] = pd.to_datetime(final_df['time'])
    # final_df = final_df[final_df['time'].dt.date.astype(str).isin([date_string])]

    final_output = 'data/output'
    os.makedirs(final_output, exist_ok=True)

    output_file_path = os.path.join(final_output, f"{date_string}_output_{len(final_df)}.csv")
    final_df.to_csv(output_file_path, index=False)
    print("[INFO] Complete")