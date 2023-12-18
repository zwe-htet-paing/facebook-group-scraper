# Facebook Scraper

Scrape data from facebook group using selenium and beautifulsoup library.

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Usage](#usage)

## Introduction

This project is designed to crawl data from facebook groups using selenium and beautifulsoup library.

## Requirements

- Chrome browser and driver
    - https://www.google.com/chrome/
    - https://sites.google.com/chromium.org/driver/
- Poetry 
    - https://python-poetry.org/docs/

## Getting Started

To get started with the Facebook scraper, follow these steps:

1. Clone this repository to your local machine.

2. Navigate to the project directory.

3. Install dependencies using Poetry

    `poetry config virtualenvs.in-project true` # to install inside project folder

    `poetry install --only main` # install dependencies


## Usage

### Test

To run the test, change `group_id` in `main.py`.

Then use the following command:

```bash
poetry run python main.py
```


Make sure to check the output CSV file after running the test.

### Run

To run the scraper, follow these steps:

1. Adjust parameters in nayar_scraper.py:

    - `resume`: Set to True to resume groups.
    - `posts_lookup`: Specify the number of posts to look up in each group.
    - `date_string`: Set the date of posts you want to retrieve.
    - `extra_date_list`: Provide a list of extra dates you want to include.
    - `credentials`: Add your Facebook credentials.
    - `driver_location`: Specify the location of the Chrome driver.
    - `output_path`: The ouput folder path.
    
2. Run the scraper using the command:

    ```bash
    ./run.sh
    ```
