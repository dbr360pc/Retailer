from CommonLib import WeeklyLib,ProductsLib
from Retailer.MongoLib import MongoLib
import time


MAX_RETRIES,RETRY_DELAY = 5,5

def getWeeklyData(retail_url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            weekly_lib = WeeklyLib(retail_url)
            weekly_fetch_result = weekly_lib.fetch_data()
            if not weekly_fetch_result['status']:
                return weekly_fetch_result
            
            result_data = weekly_fetch_result['data']
            for each_data in result_data:
                MongoLib().get_collection('product_module_products').insert_one(each_data)
            
            return {'status': True,'message': f'Total {len(result_data)} weekly products fetched and saved to database'}
        
        except Exception as e:
            retries += 1
            if retries >= MAX_RETRIES:
                return {'status': False, 'message': f"Failed after {MAX_RETRIES} attempts: {str(e)}"}
            time.sleep(RETRY_DELAY)
    

def getProductsData(retail_url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            products_lib = ProductsLib(retail_url)
            products_fetch_result = products_lib.fetch_data()
            if not products_fetch_result['status']:
                return products_fetch_result

            result_data = products_fetch_result['data']
            for each_data in result_data:
                MongoLib().get_collection('product_module_products').insert_one(each_data)

            return {'status': True,'message': f'Total {len(result_data)} products fetched and saved to database'}

        except Exception as e:
            retries += 1
            if retries >= MAX_RETRIES:
                return {'status': False,'message': f"Failed after {MAX_RETRIES} attempts: {str(e)}"}
            time.sleep(RETRY_DELAY)

