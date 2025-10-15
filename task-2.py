
from bs4 import BeautifulSoup
import requests
import sys
import os

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# desktop user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

headers = {"user-agent": USER_AGENT}
r = requests.get("https://www.elgiganten.se/tv-ljud-smart-hem/tv-tillbehor/tv?redirectquery=tv", headers=headers)

print("Status code: ", r.status_code)

if r.status_code == 200:
    # resp = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
else:
    print("Code is not valid")
    sys.exit(0)

# finds each product from the store page
containers = soup.find("ul", {"class": "w-full max-w-screen grid grid-flow-row-dense grid-cols-1 xs:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 2xl:grid-cols-4 2xl:grid-flow-cols-5"})

container = containers.find_all("li")

# name the output file to write to local disk
out_filename = "output/price.csv"
# header of csv file to be written
headers = "Product,Price \n"

# opens file, and writes headers
f = open(out_filename, "w")
f.write(headers)

# loops over each product and grabs attributes about
# each product
for con in container:

    # Get product name
    anchors = con.find_all('h2', {"class": "font-regular font-bold text-balance break-words text-lg leading-6 line-clamp-3 lg:line-clamp-2"})
    
    # Get price
    price_element = con.find("span", {"class": "font-headline text-[2.875rem] leading-[2.875rem] inc-vat"})
    
    if anchors and price_element:
        product_name = anchors[0].text.strip()
        price = price_element.text.strip().replace('.-', '').replace(' ', '')
        print(f"Product: {product_name}")
        print(f"Price: {price}")
        # Write to CSV
        f.write(f"{product_name},{price}\n")


f.close()  # Close the file

