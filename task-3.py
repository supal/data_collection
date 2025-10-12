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
import re

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
        self.TIMEDATA_URL = "https://www.timeanddate.com/"
        self.WEATHER_URL = "https://weather.com"
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
            cred = credentials.Certificate('hda-data-collection.json')
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

    def parse_time_and_date(self, soup):
        """Parse time and date information from the webpage"""
        try:
            data = {
                'source': None,
                'current_time': None,
                'city': None,
                'temperature': None,
                'weather': None
            }

            # Extract City and Weather
            box_elements = soup.find_all('div', {'class': 'tad-explore-box__content'})
            if(box_elements):
                weather = box_elements[5].find('a').get('title')
                match = re.search(r"Weather in ([^:]+): (.+)", weather)
                if match:
                    city = match.group(1).strip()
                    weather = match.group(2).strip()
                    print("City:", city)
                    print("Weather:", weather)
                    data['weather'] = weather
                    data['city'] = city
                else:
                    print("No match found")

            # Extract Temperature
            temp_element = soup.find('span', {'class': 'cur-temp nw'});
            if temp_element:
                data['temperature'] = temp_element.text.strip()

            return data
        except Exception as e:
            logging.error(f"Failed to parse time data: {str(e)}")
            raise

    def parse_weather(self, soup):
        """Parse time and date information from the webpage"""
        try:
            data = {
                'source': None,
                'current_time': None,
                'city': None,
                'temperature': None,
                'weather': None
            }


            cities_element = soup.find_all('h1', {'class': 'CurrentConditions--location--yub4l'})
            if(cities_element):
                city_element = cities_element[0]
                if city_element:
                    data['city'] = city_element.text.strip()

            temperature_element = soup.find_all('span', {'class': 'CurrentConditions--tempValue--zUBSz'})[0]
            data['temperature'] = temperature_element.text.strip()

            weather_element = soup.find_all('div', {'class': 'CurrentConditions--phraseValue---VS-k'})[0]
            data['weather'] = weather_element.text.strip()

            return data
        except Exception as e:
            logging.error(f"Failed to parse time data: {str(e)}")
            raise

    def save_to_local(self, data):
        """Save data to local JSON file with updates"""
        try:
            filename = os.path.join(self.output_dir, "weather_data.json")
            all_data = []
            
            # Read existing data if file exists
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        all_data = json.load(f)
                        if not isinstance(all_data, list):
                            all_data = [all_data]
                except json.JSONDecodeError:
                    all_data = []
            
            # Add new data to the list
            all_data.append(data)
            
            # Write updated data back to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4)
            print(f"Data updated in {filename}")
        except Exception as e:
            print(f"Error saving to local file: {str(e)}")
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
            response = self.fetch_webpage(self.TIMEDATA_URL)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract data
            data = self.parse_time_and_date(soup)

            # Add source
            data['source'] = self.TIMEDATA_URL

            # Add timestamp
            data['current_time'] = datetime.now().isoformat()
            
            # Save data locally
            self.save_to_local(data)
            
            # Save data to Firebase
            self.save_to_firebase(data)

            # Fetch webpage
            response = self.fetch_webpage(self.WEATHER_URL)

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract data
            data = self.parse_weather(soup)

            # Add source
            data['source'] = self.WEATHER_URL

            # Add timestamp
            data['current_time'] = datetime.now().isoformat()

            # Save data locally
            self.save_to_local(data)

            # Save data to Firebase
            self.save_to_firebase(data)

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