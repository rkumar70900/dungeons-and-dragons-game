"""
Automates the process of scraping monster data from the 5esrd.com website using Playwright.

Args:
    playwright (Playwright): The Playwright instance used to control the browser.

Steps:
    1. Launches a Chromium browser in non-headless mode.
    2. Navigates to the 5esrd.com website.
    3. Handles pop-up dialogs by clicking "OK, Don't show this again" and "OK" buttons.
    4. Navigates to the "Monsters Database" page.
    5. Extracts all anchor tags within the first column of the table with id 'archive-data-table'.
    6. Iterates through each extracted link, navigates to the link, and scrapes the monster characteristics.
    7. Saves the scraped data to a text file named after the monster.
    8. Closes the browser and context.

Note:
    Ensure that the necessary dependencies (Playwright) are installed and properly configured.
"""
import re, time, os
from playwright.sync_api import Playwright, sync_playwright, expect

stories = {}

files = os.listdir('C://Users//rajes//OneDrive//Documents//GitHub//dnd_start//web_scraping')

def run(playwright: Playwright) -> None:
    """
    Automates the process of scraping monster data from the 5esrd.com website using Playwright.
    Args:
        playwright (Playwright): The Playwright instance used to control the browser.
    Steps:
        1. Launches a Chromium browser in non-headless mode.
        2. Navigates to the 5esrd.com website.
        3. Handles pop-up dialogs by clicking "OK, Don't show this again" and "OK" buttons.
        4. Navigates to the "Monsters Database" page.
        5. Extracts all anchor tags within the first column of the table with id 'archive-data-table'.
        6. Iterates through each extracted link, navigates to the link, and scrapes the monster characteristics.
        7. Saves the scraped data to a text file named after the monster.
        8. Closes the browser and context.
    Note:
        Ensure that the necessary dependencies (Playwright) are installed and properly configured.
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.5esrd.com/")
    time.sleep(2)
    page.get_by_role("button", name="OK, Don't show this again").click()
    time.sleep(2)
    page.get_by_role("button", name="OK").click()
    time.sleep(2)
    page.get_by_role("link", name="Monsters Database").click()
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
