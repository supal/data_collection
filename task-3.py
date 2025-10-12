#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import requests
import sys
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

class TimeDataScraper:
    def __init__(self):
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        self.BASE_URL = "https://www.timeanddate.com/"
        self.headers = {"user-agent": self.USER_AGENT}
        
        # Create output directory if it doesn't exist
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Initialize Firebase
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Initialize Firebase with your credentials
            # You need to replace 'path/to/your/serviceAccountKey.json' with your actual Firebase credentials file
            cred = credentials.Certificate('hda-data-collection-a345d38189b5.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://hda-data-collection-default-rtdb.firebaseio.com/'
            })
            logging.info("Firebase initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
            raise

    def fetch_webpage(self, url):
        """Fetch webpage content with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Failed to fetch webpage: {str(e)}")
            raise

    def parse_time_data(self, soup):
        """Parse time and date information from the webpage"""
        try:
            data = {
                'current_time': None,
                'timezone': None,
                'date': None,
                'weather': None
            }
            
            # Extract current time
            time_element = soup.find('span', {'id': 'ct'})
            if time_element:
                data['current_time'] = time_element.text.strip()

            # Extract timezone
            timezone_element = soup.find('span', {'id': 'ctz'})
            if timezone_element:
                data['timezone'] = timezone_element.text.strip()

            # Extract current date
            date_element = soup.find('span', {'id': 'cd'})
            if date_element:
                data['date'] = date_element.text.strip()

            # Extract Weather
            box_elements = soup.find_all('div', {'class': 'tad-explore-box__content'})
            if(box_elements):
                weather = box_elements[5].find('a').get('title')
                data['weather'] = weather

            # Extract Temperature
            temp_element = soup.find('span', {'class': 'cur-temp nw'});
            if temp_element:
                data['temperature'] = temp_element.text.strip()

            return data
        except Exception as e:
            logging.error(f"Failed to parse time data: {str(e)}")
            raise

    def save_to_local(self, data):
        """Save data to local file"""
        try:
            filename = os.path.join(self.output_dir, f"time_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logging.info(f"Data saved locally to {filename}")
        except Exception as e:
            logging.error(f"Failed to save data locally: {str(e)}")
            raise

    def save_to_firebase(self, data):
        """Save data to Firebase"""
        try:
            # Create a reference to the database
            ref = db.reference('time_data')
            # Push data to Firebase
            ref.push(data)
            logging.info("Data saved to Firebase successfully")
        except Exception as e:
            logging.error(f"Failed to save data to Firebase: {str(e)}")
            raise

    def run(self):
        """Main execution method"""
        try:
            # Fetch webpage
            response = self.fetch_webpage(self.BASE_URL)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract data
            data = self.parse_time_data(soup)
            
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            # Save data locally
            self.save_to_local(data)
            
            # Save data to Firebase
            # self.save_to_firebase(data)
            
            logging.info("Data collection completed successfully")
            return data
            
        except Exception as e:
            logging.error(f"Error in main execution: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        scraper = TimeDataScraper()
        data = scraper.run()
        print("Scraped data:", json.dumps(data, indent=2))
    except Exception as e:
        logging.error(f"Application failed: {str(e)}")
        sys.exit(1)