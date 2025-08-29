from metro.CommonLib import CommonLib
from MongoLib import MongoLib

def getProductsData(retail_url):
    
    try:

        commonlib = CommonLib(retail_url)
        
        products_fetch_result = commonlib.PhaseTwo()
        if not products_fetch_result['status']:
            return products_fetch_result
        
        result_data = products_fetch_result['data']

        for each_data in result_data:
            MongoLib().get_collection('product_module_products').insert_one(each_data)

        return {'status': True, 'message': f'Total {len(result_data)} products fetched and saved to database'}
    
    except Exception as e:
        return {'status': False, 'message': str(e)}

