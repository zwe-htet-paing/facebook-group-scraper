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

`poetry run python main.py`
