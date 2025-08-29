from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import requests
import uuid
import time
import json

class WeeklyLib:

    def __init__(self,url=None):

        self.pagination_url = url

    
    def startDriver(self):
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        desired_capabilities['pageLoadStrategy'] = 'normal'

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--auto-open-devtools-for-tabs")
        options.add_argument("--ignore-certificate-errors")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        return driver


    def fetch_data(self):
        
        pagination_url = self.pagination_url
        if not pagination_url:
            return {'status': False, 'message': 'Pagination URL not found'}

        driver,all_products_url = None,None

        for _ in range(10):

            try:

                driver = self.startDriver()

                driver.get(pagination_url)

                time.sleep(10)

                logs = driver.get_log("performance")

                all_products_url = ""
                for log in logs:
                    network_log = json.loads(log["message"])["message"]
                    if ("Network.response" in network_log["method"] or "Network.request" in network_log["method"] or "Network.webSocket" in network_log["method"]) :
                        if network_log.get('method') == 'Network.responseReceived' and 'flyerkit/publication/' in network_log.get('params', {}).get('response', {}).get('url', ''):
                            all_products_url = network_log.get('params', {}).get('response', {}).get('url', '')
                            if all_products_url:
                                break

                if all_products_url:
                    break

            except Exception as e:
                print(f"Retrying due to error")
                if driver:
                    driver.quit()
                time.sleep(10)
                continue

        if not all_products_url:
            if driver:
                driver.quit()
            return {'status': False,'message': 'Could not find the products URL in network logs'}

        req = requests.get(all_products_url)
        if req.status_code != 200:
            if driver:
                driver.quit()
            return {'status': False,'message': f'Failed to fetch data from {all_products_url}, status code: {req.status_code}'}

        response_data = req.json()

        if driver:
            driver.quit()

        result_data = []
        for each_response in response_data:
            if each_response['price_text']:
                each_obj = {
                    'uid': str(uuid.uuid4()),
                    'market_name': 'ALBERTSON',
                    'scraper_type': 'weekly',
                    'product_id': str(each_response.get('id', '')),
                    'brand_name': each_response.get('brand', ''),
                    'product_name': each_response.get('name', ''),
                    'description': each_response.get('description', ''),
                    'product_details':{
                        'original_price' : '$' + each_response.get('original_price', '') if each_response.get('original_price', '') else '',
                        'price': '$' + each_response.get('price_text', ''),
                        'selling_size': each_response.get('selling_size', ''),
                        'quantity_unit': each_response.get('post_price_text', ''),
                        'valid_from': each_response.get('valid_from', ''),
                        'valid_to': each_response.get('valid_to', ''),
                        'product_url': each_response.get('item_web_url',''),
                        'category': [],
                    },
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }

                for each_cat in each_response['categories']:
                    each_obj['product_details']['category'].append(each_cat)

                result_data.append(each_obj)

        return {'status': True,'message':'Data has been processed.','data': result_data}

class ProductsLib:

    def __init__(self,url=None):

        self.pagination_url = url

    
    def fetch_data(self):

        return {'status': True, 'message': 'Not implemented yet', 'data': []}