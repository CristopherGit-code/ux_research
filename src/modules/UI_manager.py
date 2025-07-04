from .config import Settings
from .db import DataBase
from .file_handler import File_handlder
from .oci_client import Client
import logging,uuid

logger = logging.getLogger(name=f'File.{__name__}.UI')

class UI:
    def __init__(self):
        self.merged_data = ''
        self.merged_files_db = {}

        self.settings = Settings("ux.yaml")
        self.db = DataBase(self.settings)
        self.client = Client(self.settings)
        self.file_manager = File_handlder()

    def load_user_session(self,session):
        user_id = uuid.uuid4()
        session = user_id    
        return session
    
    def _get_user_filter_files(self,user_id):
        try:
            return self.merged_files_db[user_id]
        except KeyError as k:
            return ''

    def _manage_user_filter_files(self,user_id,content):
        user_files = self._get_user_filter_files(user_id)
        if not user_files:
            self.merged_files_db[user_id] = ''
        self.merged_files_db[user_id] = content
    
    def _manage_filter(self,year,type,region,customer,product, user_id):
        responses = self.db.get_db_response(['t.metadata.file_name','t.content'],year,type,region,customer,product)
        if not responses:
            self.merged_data = 'No data, retry'
            return ['No files found with that filter']
        else:
            self.merged_data = self.file_manager.merge_md(responses[1])
            self._manage_user_filter_files(user_id, self.merged_data)
            return responses[0]
        
    def get_client_analysis(self,prompt,message_history,system_instructions, user_id):
        query = prompt + f' given the data in {self._get_user_filter_files(user_id)}'
        response = self.client.provide_analysis(query, system_instructions, user_id)
        return response

    def get_client_filter(self,year,type,region,customer,product, prompt:str, user_id, file_list):
        if not prompt:
            lists = self._manage_filter(year,type,region,customer,product, user_id)
            message = f'Filtered manually by: {[year,type,region,customer,product]}'
            
            return lists, message
        r_dict = self.client.filter_files(prompt)
        #logger.debug(r_dict)
        year_p = r_dict[0]
        type_p = r_dict[1]
        region_p = r_dict[2]
        customer_p = r_dict[3]
        product_p = r_dict[4]
        lists = self._manage_filter(year_p,type_p,region_p,customer_p,product_p, user_id)
        message = f'Filter applied to prompt: {r_dict}'
        
        return lists,message
    
    def available_filters(self):
        responses = self.db.get_db_response(
            ['t.metadata.report_date','t.metadata.type','t.metadata.regions[0].region']
        )
        years = [int(date[:4]) for date in responses[0]]
        years.insert(0,2010)
        unique_years = sorted(set(years))

        responses[1].insert(0,"")
        unique_type = sorted(set(responses[1]))

        responses[2].insert(0,"")
        unique_region = sorted(set(responses[2]))

        return unique_years,unique_type,unique_region
    
    def manage_files(self,new_files):
        return 'Pass'
    
    def get_chat_placeholder(self):
        return self.settings.chat_placeholder