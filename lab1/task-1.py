#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import requests
import sys
import os

# desktop user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
URL1 = "https://www.technologyreview.com/2025/10/07/1124998/the-three-big-unanswered-questions-about-sora/"
URL2 = "https://www.sciencedaily.com/releases/2025/10/251010091546.htm"

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# name the output file to write to local disk
out_filename = "output/task-1.txt"
f = open(out_filename, "w")

f.write("Task 1: Web Scraping: Artificial Intelligence\n")
f.write("===================\n\n")
f.write("Source:")
f.write(URL1 + "\n")
f.write("----------------------------------------------------------------------------------------\n\n")


headers = {"user-agent": USER_AGENT}
r = requests.get(URL1, headers=headers)

print("Status code: ", r.status_code)

if r.status_code == 200:
    soup = BeautifulSoup(r.content, "html.parser")
else:
    print("Scrapping is not possible")
    sys.exit(0)

# Article 1
heading_element = soup.find("h1",{"class":"contentArticleHeader__title--4ba85d49e1a4385c0496cbbb5900641b"})
title = heading_element.text
body_element = soup.find("div",{"class":"contentBody__content--42a60b56e419a26d9c3638a9dab52f55"})
body = body_element.text
print(title)
f.write("Heading: " + title + "\n\n")
f.write("Content: " + body + "\n")


f.write("\n\n")
f.write("Source:")
f.write(URL2 + "\n")
f.write("----------------------------------------------------------------------------------------\n\n")

# Article 2
r = requests.get(URL2, headers=headers)

print("Status code: ", r.status_code)

if r.status_code == 200:
    soup = BeautifulSoup(r.content, "html.parser")
else:
    print("Scrapping is not possible")
    sys.exit(0)


heading_element = soup.find("h1",{"headline"})
title = heading_element.text
body_element = soup.find("div",{"id":"text"})
body = body_element.text
print(title)
f.write("Heading: " + title + "\n\n")
f.write("Content: " + body + "\n")

f.close() # Close the file


