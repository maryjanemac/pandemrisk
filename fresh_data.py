from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv

with open('geo-data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        print(row)

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/Users/lzy/bin/chromedriver')

url = "https://www.eventbrite.com/directory/sitemap/"
driver.get(url)

elements = driver.find_elements_by_css_selector(".panel_head2")
e_groups = [el.find_elements_by_css_selector(".g-group") for el in elements if el.find_element_by_css_selector("h2").text == "United States"]
e_links_nested = [[el.find_elements_by_css_selector(".g-cell") for el in els] for els in e_groups]
e_links = [e.find_element_by_css_selector("a").get_attribute("href") for els in e_links_nested for el in els for e in el]

print(e_links)