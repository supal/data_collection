#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import requests
import sys
import os

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# name the output file to write to local disk
out_filename = "output/task-1.txt"


# desktop user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

headers = {"user-agent": USER_AGENT}
r = requests.get("https://www.technologyreview.com/2025/10/07/1124998/the-three-big-unanswered-questions-about-sora/", headers=headers)

print("Status code: ", r.status_code)

if r.status_code == 200:
    soup = BeautifulSoup(r.content, "html.parser")
else:
    print("Scrapping is not possible")
    sys.exit(0)

# Article 1
heading_element = soup.find("h1",{"class":"contentArticleHeader__title--4ba85d49e1a4385c0496cbbb5900641b"})
f = open(out_filename, "w")
title = heading_element.text
body_element = soup.find("div",{"class":"contentBody__content--42a60b56e419a26d9c3638a9dab52f55"})
body = body_element.text

print(title)
print(body)

f.write(title + "\n")
f.write(body + "\n")

f.close() # Close the file


