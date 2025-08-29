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
        
        driver, all_products_url = None, None

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
                    'market_name': 'ALDI',
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

        self.product_url = url
        if not self.product_url:
            print("URL not found")
            return {'status': False, 'message': 'Product URL not found'}

        self.category_key = self.product_url.split('/')[-1]
        if not self.category_key.isdigit():
            print("Invalid category key in URL")
            return {'status': False, 'message': 'Invalid category key in URL'}
        
        self.product_api_url = "https://api.aldi.us/v3/product-search?currency=USD&serviceType=pickup&categoryKey={category_key}&limit=60&offset={offset}&sort=name_asc&servicePoint=440-018"

    def fetch_data(self):
        page_no,result_data = 1,[]
        while True:
            offset = (page_no - 1) * 60
            print(f"Fetching page {page_no}...")

            each_product_api_url = self.product_api_url.format(category_key=self.category_key, offset=offset)
            req = requests.get(each_product_api_url)
            response_data = req.json()

            if 'data' not in response_data:
                print("No data found in the response")
            else:
                totalCount = response_data.get('meta',{}).get('pagination',{}).get('totalCount', 0)
                for each_product in response_data['data']:
                    each_product_id = each_product.get('sku')
                    category_data = each_product.get('categories', [])

                    each_obj = {
                        'uid': str(uuid.uuid4()),
                        'market_name': 'ALDI',
                        'scraper_type': 'product',
                        'product_id': each_product_id,
                        'product_name': each_product.get('name'),
                        'brand_name': each_product.get('brandName') if each_product.get('brandName') else '',
                        'description': '',
                        'product_details': {
                            'selling_size': each_product.get('sellingSize'),
                            'original_price': '',
                            'price': each_product.get('price', {}).get('amountRelevantDisplay'),
                            'quantity_unit': each_product.get('quantityUnit'),
                            'valid_from' : each_product.get('validFrom',''),
                            'valid_to' : each_product.get('validTo',''),
                            'product_url': 'https://www.aldi.us/product/' + each_product.get('urlSlugText') + '-' + each_product_id,
                            'category': [],
                        },
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }

                    for each_category in category_data:
                        if each_category.get('name', ''):
                            each_obj['product_details']['category'].append(each_category.get('name', ''))

                    each_detail_url = f'''https://api.aldi.us/v2/products/{each_product_id}?servicePoint=440-018&serviceType=pickup'''
                    each_detail_req = requests.get(each_detail_url)
                    if each_detail_req.status_code == 200:
                        each_detail_data = each_detail_req.json()
                        if 'data' in each_detail_data:
                            each_obj['description'] = each_detail_data['data'].get('description')

                    result_data.append(each_obj)

            page_no += 1
            if totalCount <= (offset + 60):
                break
        
        return {'status': True, 'message': 'Data has been fetched successfully.', 'data': result_data}