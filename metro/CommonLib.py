from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse,urlunparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime
import uuid
import random
import time
import re


MAX_RETRIES,RETRY_DELAY,NO_OF_THREADS = 5,5,3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.3; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]


def clean_text(text):
    """
    Cleans the input text by removing extra spaces and non-breaking spaces.
    """
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()


def getData(soup,url,product_id,product_name):
    ul_list = soup.select_one('ul.b--list')
    li_elements = ul_list.find_all('li')
    nav_list = []
    for li in li_elements:
        nav_list.append(li.get_text(strip=True)) 
    nav_list = nav_list[3:]
    if len(nav_list) == 4:
        Aisle = nav_list[0]
        Department = nav_list[1]
        Category = nav_list[2]
        Subcategory = nav_list[3]
    elif len(nav_list) == 3:
        Aisle = nav_list[0]
        Department = nav_list[1]
        Category = nav_list[2]
        Subcategory = nav_list[2]
    elif len(nav_list) == 2:
        Aisle = nav_list[0]
        Department = nav_list[1]
        Category = nav_list[1]
        Subcategory = nav_list[1]
    else:
        Aisle = nav_list[0]
        Department = nav_list[0]
        Category = nav_list[0]
        Subcategory = nav_list[0]

    brand_name_obj = soup.select_one(f'div[data-product-code="{product_id}"] div.pi--brand')
    brand_name = clean_text(brand_name_obj.get_text(strip=True) if brand_name_obj else "")

    weight_obj = soup.select_one(f'div[data-product-code="{product_id}"] div.pi--weight')
    weight = clean_text(weight_obj.get_text(strip=True) if weight_obj else "")
    
    before_price,before_price_abbr = '',''
    before_price_obj = soup.select(f'div[data-product-code="{product_id}"] div.pricing__before-price')
    for each_before in before_price_obj:
        for each_span in each_before.find_all('span'):
            if each_span.has_attr('class'):
                each_span['class'] = ' '.join(each_span['class'])
                if each_span['class'] == 'invisible-text':
                    continue
            if each_span.find('abbr'):
                before_price_abbr_obj = clean_text(each_span.get_text(strip=True))
                if '/' in before_price_abbr_obj:
                    before_price_abbr_obj = before_price_abbr_obj.split('/')[-1].strip()  
                before_price_abbr += before_price_abbr_obj 
            else:
                before_price += clean_text(each_span.get_text(strip=True))

    
    promo_price_obj = soup.select(f'div[data-product-code="{product_id}"] div.pricing__sale-price.promo-price')
    if not len(promo_price_obj):
        promo_price_obj = soup.select(f'div[data-product-code="{product_id}"] div.pricing__sale-price')
    promo_price,promo_price_abbr = '',''
    for each_promo in promo_price_obj:
        for each_span in each_promo.find_all('span'):
            if each_span.find('abbr'):
                promo_price_abbr_obj = clean_text(each_span.get_text(strip=True))
                if '/' in promo_price_abbr_obj:
                    promo_price_abbr_obj = promo_price_abbr_obj.split('/')[-1].strip()
                promo_price_abbr += promo_price_abbr_obj
            else:
                promo_price += clean_text(each_span.get_text(strip=True))


    second_price_obj = soup.select(f'div[data-product-code="{product_id}"] div.pricing__secondary-price.promo-price')
    if not len(second_price_obj):
        second_price_obj = soup.select(f'div[data-product-code="{product_id}"] div.pricing__secondary-price')

    second_price,second_price_abbr = '',''
    for each_promo in second_price_obj:
        for each_span in each_promo.find_all('span'):
            if each_span.find('abbr'):
                second_price_abbr_obj = each_span.find('abbr').get_text(strip=True) if each_span.find('abbr') else ''
                if '/' in second_price_abbr_obj:
                    second_price_abbr_obj = second_price_abbr_obj.split('/')[-1].strip()
                second_price_abbr += second_price_abbr_obj
                each_span.find('abbr').decompose()
            second_price += clean_text(each_span.get_text(strip=True))
            break

    if 'or' in second_price:
        second_price = second_price.split('or')[-1].strip()

    if '/' in second_price:
        second_price_abbr = second_price.rsplit('/')[-1].strip() + second_price_abbr if second_price_abbr else ''
        second_price = second_price.split('/')[0].strip()

    validity_obj = soup.select_one(f'div[data-product-code="{product_id}"] div.pricing__until-date')
    validity_data = clean_text(validity_obj.get_text(strip=True) if validity_obj else "")
    validity = clean_text(validity_data.split('*')[0])
    points,points_desc = "",""
    if '*' in validity_data:
        points_data = clean_text(validity_data.split('*')[-1].strip().split('points')[0])
        points = ' '.join(re.findall(r'\d+(?:\.\d+)?', points_data) if points_data and re.findall(r'\d+(?:\.\d+)?', points_data) else "")
        points_desc = clean_text('points ' + validity_data.split('*')[-1].strip().split('points')[-1].strip()) if len(validity_data.split('*')[-1].strip().split('points')) > 1 else ""

    description_obj = soup.select_one(f'div.pi-accordion-list div.accordion--text')
    description = clean_text(description_obj.get_text(strip=True) if description_obj else "")
    ingredients_obj = soup.select_one(f'div.pi-accordion-list p.pdp-ingredients-list')
    ingredients = clean_text(ingredients_obj.get_text(strip=True) if ingredients_obj else "")

    result_obj = {
        'uid': str(uuid.uuid4()),
        'market_name': 'METRO',
        'scraper_type': 'product',
        'product_id': str(product_id),
        'brand_name': brand_name,
        'product_name': product_name,
        'description': description,
        'product_details':{
            'Aisle': Aisle,
            'Department': Department,
            'category': [Category],
            'Subcategory': Subcategory,
            'Ingredients': ingredients,
            'Pack Size / Weight': weight,
            'Pricing before Price': before_price,
            'PbP Unit': before_price_abbr.replace('.','. ').strip(),
            'price-update pi-price-promo': promo_price,
            'price-update pi-price-promo-Unit': promo_price_abbr.replace('.','. ').strip(),
            'validity': validity,
            'pricing__secondary-price promo-price': second_price,
            'pricing__secondary-price promo-price Unit': second_price_abbr.replace('.','. ').strip(),
            'Points': points,
            'Points conditions': points_desc,
            'product_url': url
        },
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    return {'status': True,'message': 'Data found','data': result_obj}


class CommonLib:

    def __init__(self,url=None):

        self.product_url = url
        if not self.product_url:
            return {'status': False, 'message': 'Product URL not found'}


    def fetchHtml(self,url,product_id,product_name):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                with sync_playwright() as playwright:
                    browser = playwright.firefox.launch(headless=True)
                    context = browser.new_context(
                        user_agent=random.choice(USER_AGENTS),
                        viewport={"width": 1280, "height": 800},
                        locale="en-US"
                    )
                    page = context.new_page()
                    page.route("**/*",lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    html = page.content()

                    context.close()
                    browser.close()
                
                soup = BeautifulSoup(html, 'html.parser')
                element = soup.select_one(f'div[data-product-code="{product_id}"]')

                if element:
                    result = getData(soup,url,product_id,product_name)
                    return result
                else:
                    retries += 1
                    time.sleep(RETRY_DELAY)

            except Exception as e:
                retries += 1
                time.sleep(RETRY_DELAY)
                    
        return {'status': False,'message': f'Failed to fetch product {product_id} after {MAX_RETRIES} retries.'}


    def GetNoOfPages(self):

        pagination_language = 'EN' if 'metro.ca/en' in self.product_url else 'FR'

        try:
            with sync_playwright() as playwright:

                browser = playwright.firefox.launch(headless=True)

                context = browser.new_context(user_agent=random.choice(USER_AGENTS),viewport={"width": 1280, "height": 800},locale="en-US")
                
                page = context.new_page()

                page.route("**/*",lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"]else route.continue_())

                page.goto(self.product_url, wait_until="domcontentloaded", timeout=60000)

                html = page.content()

                context.close()
                browser.close()
                
            soup = BeautifulSoup(html, 'html.parser')

            if pagination_language == 'EN':
                selector = 'a.ppn--element[aria-label="go to last page"]'
            else:
                selector = 'a.ppn--element[aria-label="aller à la dernière page"]'

            pagination_elements = soup.select(selector)

            if not pagination_elements:
                return {'status': True, 'pages': 1}

            pagination_element = int(pagination_elements[-1].text)

            return {'status': True, 'pages': pagination_element}

        except Exception as e:
            return {'status': False, 'message': f"Error in GetNoOfPages: {str(e)}"}


    def GetPaginationData(self,each_url):

        retries = 0
        while retries < MAX_RETRIES:
            try:
                with sync_playwright() as playwright:

                    browser = playwright.firefox.launch(headless=True)

                    context = browser.new_context(user_agent=random.choice(USER_AGENTS),viewport={"width": 1280, "height": 800},locale="en-US")

                    page = context.new_page()

                    page.route("**/*",lambda route: route.abort()if route.request.resource_type in ["image", "stylesheet", "font"]else route.continue_())

                    page.goto(each_url, wait_until="domcontentloaded", timeout=60000)

                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')

                    context.close()
                    browser.close()
                    
                elements = soup.select(
                    'div[data-list-name="flyerEcomGrid_flyer"] div[data-unit-increment="1"], '
                    'div[data-list-name="flyerEcomGridFeatured_flyer"] div[data-unit-increment="1"]'
                )

                result_data = []

                for each_element in elements:
                    each_product_url_element = each_element.find('a')
                    each_product_url = each_product_url_element['href'] if each_product_url_element else ''
                    each_product_details = each_element.attrs
                    each_category_details = each_product_details.get('data-ec-category')

                    if each_product_details and each_category_details and each_product_url:
                        each_obj = {
                            'product_id': each_product_details.get('data-product-code', ''),
                            'product_name': each_product_details.get('data-product-name', ''),
                            'product_group': each_product_details.get('data-product-name', ''),
                            'product_url': 'https://www.metro.ca' + each_product_url
                        }
                        result_data.append(each_obj)

                return {'status': True, 'data': result_data}

            except Exception as e:
                retries += 1
                time.sleep(RETRY_DELAY)

        return {'status': False, 'message': f"Failed to fetch data from {each_url} after {MAX_RETRIES} retries."}

    def update_pagination_url(self,pagination_url, each_page):

        parsed_url = urlparse(pagination_url)
        
        path = parsed_url.path
        
        last_element = path.strip('/').split('/')[-1]
        
        if re.search(rf'{last_element}-page-\d+', path):
            new_path = re.sub(rf'{last_element}-page-\d+', f'{last_element}-page-{each_page}', path)
        else:
            new_path = re.sub(rf'{last_element}', f'{last_element}-page-{each_page}', path)
        
        updated_url = urlunparse((parsed_url.scheme,parsed_url.netloc,new_path,parsed_url.params,parsed_url.query,parsed_url.fragment))
        
        return updated_url
        

    def PhaseOne(self,pagination_url):

        pagination_data = self.GetNoOfPages()
        if not pagination_data['status']:
            return pagination_data

        url_data,no_of_pages = [],pagination_data['pages']

        for each_page in range(1, no_of_pages + 1):
            each_url = self.update_pagination_url(pagination_url, each_page)
            url_data.append(each_url)

        results = []
        with ThreadPoolExecutor(max_workers=NO_OF_THREADS) as executor:
            for result in executor.map(self.GetPaginationData, url_data):
                results.extend(result['data'] if result['status'] else [])
                
        unique_data,unique_product_id_data = [],[]
        for item in results:
            pid = item['product_id']
            if pid not in unique_product_id_data:
                unique_product_id_data.append(pid)
                unique_data.append(item)
                        
        return {'status': True,'message': 'Data has been processed.','data': unique_data}
    
    def PhaseTwo(self):

        all_products_result = self.PhaseOne(self.product_url)
        if not all_products_result['status']:
            return {'status': False, 'message': all_products_result['message']}

        all_products_data = all_products_result['data']

        results = []
        with ThreadPoolExecutor(max_workers=NO_OF_THREADS) as executor:
            futures = [executor.submit(self.fetchHtml, each['product_url'], each['product_id'], each['product_name']) for each in all_products_data]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result['status']:
                        results.append(result['data'])
                except Exception as e:
                    print(f"Error during future execution: {e}")

        return {'status': True,'message': 'Data has been processed.','data': results}