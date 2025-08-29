import argparse
from aldi import Main as AldiMain
from albertson import Main as AlbertMain
from metro import Main as MetroMain
from MongoLib import MongoLib
import datetime


parser = argparse.ArgumentParser(prog='tool',formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=550, width=500),description="Retailer Framework")

parser.add_argument('-t', '--task_id',dest="task_id", help='Id of the task want to run')
    
parser.add_argument('-r', '--retail', dest='retail', help='Name of the retail')

parser.add_argument('-s', '--scraper', dest='scraper', help='Name of the scraper in the retail')

parser.add_argument('-u', '--url', dest='url',help='Input url')


args, extra_args = parser.parse_known_args()

scrap_result = {'status': False,'message': 'Invalid parameters'}

if __name__ == "__main__":

    task_id,retail_name,scraper_type,retail_url = args.task_id,args.retail,args.scraper,args.url

    if retail_name.lower() == 'aldi':
        if scraper_type.lower() == 'weekly':
            scrap_result = AldiMain.getWeeklyData(retail_url)
        elif scraper_type.lower() == 'product':
            scrap_result = AldiMain.getProductsData(retail_url)
        else:
            scrap_result = {'status': False,'message': 'Invalid scraper type'}
        
    elif retail_name.lower() == 'albertson':
        if scraper_type.lower() == 'weekly':
            scrap_result = AlbertMain.getWeeklyData(retail_url)
        elif scraper_type.lower() == 'product':
            scrap_result = AlbertMain.getProductsData(retail_url)
        else:
            scrap_result = {'status': False,'message': 'Invalid scraper type'}
    
    elif retail_name.lower() == 'metro':
        if scraper_type.lower() == 'product':
            scrap_result = MetroMain.getProductsData(retail_url)
        else:
            scrap_result = {'status': False,'message': 'Invalid scraper type'}

    else:
        scrap_result = {'status': False,'message': 'Invalid Retail Name'}

if MongoLib().get_collection('product_module_scheduledtask').find_one({'uid': task_id}):
    MongoLib().get_collection('product_module_scheduledtask').update_one({'uid': task_id},{'$set': {'last_run_at': datetime.datetime.now(),'status': 'Completed: ' + scrap_result['message'] if scrap_result['status'] else 'Failed: ' + scrap_result['message']}})
