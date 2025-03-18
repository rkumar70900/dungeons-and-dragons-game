import re, time, os
"""
This script uses Playwright to scrape background data from the 5e SRD website and save it to text files.
Modules:
    re: Provides regular expression matching operations.
    time: Provides various time-related functions.
    os: Provides a way of using operating system dependent functionality.
    playwright.sync_api: Provides synchronous API for Playwright.
Functions:
    run(playwright: Playwright) -> None:
        Launches a browser instance, navigates to the 5e SRD website, and scrapes background data.
        Saves the scraped data to text files if they do not already exist.
Variables:
    stories (dict): A dictionary to store the scraped data.
    files (list): A list of filenames in the specified directory.
"""
from playwright.sync_api import Playwright, sync_playwright, expect

stories = {}

files = os.listdir('C://Users//rajes//Documents//GitHub//dungeons-and-dragons-game//web_scraping')

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.5esrd.com/")
    time.sleep(2)
    page.get_by_role("button", name="OK, Don't show this again").click()
    time.sleep(2)
    page.get_by_role("button", name="OK").click()
    time.sleep(2)
    page.get_by_role("link", name="Backgrounds Database").click()
    time.sleep(2)

# Select all anchor tags within the first column of the table with id 'races'
    hrefs = page.eval_on_selector_all(
        "#archive-data-table td:first-child a",
        "elements => elements.map(el => el.href)"
    )
    time.sleep(2)
    print("Links in the first column:", hrefs)
    for href in hrefs:
        name = href.split('/')[-2] 
        file = name + '.txt'
        if file in files:
            continue
        page.goto(href)
        race_characteristics = page.locator('//*[@id="article-content"]').inner_text()
         
        with open(name + ".txt", "w", encoding="utf-8") as file:
            file.write(str(race_characteristics))
        time.sleep(2)
    browser.close()
    context.close()



with sync_playwright() as playwright:
    run(playwright)
