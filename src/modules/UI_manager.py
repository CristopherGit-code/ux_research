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
    
    def _manage_filter(self,study,location,utility,property_type,characteristics,products,events,chat_init_uuid):
        responses = self.db.get_db_response(['t.metadata.utility','t.file_name'],study,location,utility,property_type,characteristics,products,events)
        if not responses:
            self.merged_data = 'No data, retry'
            return ['No files found with that filter']
        else:
            # self.merged_data = self.file_manager.merge_md(responses[1])
            # self._manage_user_filter_files(chat_init_uuid, self.merged_data)
            return responses[0]
        
    def get_client_analysis(self,prompt,message_history,system_instructions, user_id):
        query = prompt + f' given the data in {self._get_user_filter_files(user_id)}'
        response = self.client.provide_analysis(query, system_instructions, user_id)
        return response

    def get_client_filter(self,study,location,utility,property_type,characteristics,products,events,text_search,chat_init_uuid):
        if not text_search:
            lists = self._manage_filter(study,location,utility,property_type,characteristics,products,events,chat_init_uuid)
            message = f'Filtered manually by: {[study,location,utility,property_type,characteristics,products,events]}'
            
            return lists, message
        r_dict = self.client.filter_files(text_search)
        #logger.debug(r_dict)
        year_p = r_dict[0]
        type_p = r_dict[1]
        region_p = r_dict[2]
        customer_p = r_dict[3]
        product_p = r_dict[4]
        lists = self._manage_filter(year_p,type_p,region_p,customer_p,product_p, chat_init_uuid)
        message = f'Filter applied to prompt: {r_dict}'
        
        return lists,message
    
    def available_filters(self):
        responses = self.db.get_db_response(
            ['t.metadata.study','t.metadata.regions[0].region','t.metadata.utility','t.metadata.property_type','t.metadata.participant_characteristics']
        )
        [[{'characteristic': 'Female'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Female'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Female'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Male'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Female'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Female'}, {'characteristic': 'Renter'}, {'characteristic': 'Low income'}], [{'characteristic': 'Female'}, {'characteristic': 'Homeowner'}, {'characteristic': 'Smart home user'}], [{'characteristic': 'Female'}, {'characteristic': 'Homeowner'}, {'characteristic': 'Smart home user'}], [{'characteristic': 'Female'}, {'characteristic': 'Homeowner'}, {'characteristic': 'Smart home user'}], [{'characteristic': 'Female'}, {'characteristic': 'Homeowner'}, {'characteristic': 'Smart home user'}], [{'characteristic': 'Male'}, {'characteristic': 'Homeowner'}, {'characteristic': 'Smart home user'}]]
        characteristics_list = list({characteristic['characteristic'] for response in responses[4] for characteristic in response})
        unique_characteristics = sorted(set(characteristics_list))
        unique_characteristics.insert(0,"Select")
        unique_study = sorted(set(responses[0]))
        unique_study.insert(0,"Select")
        unique_region = sorted(set(responses[1]))
        unique_region.insert(0,"Select")
        unique_utility = sorted(set(responses[2]))
        unique_utility.insert(0,"Select")
        unique_property_type = sorted(set(responses[3]))
        unique_property_type.insert(0,"Select")

        return unique_study,unique_region,unique_utility,unique_property_type,unique_characteristics
    
    def manage_files(self,new_files):
        return 'Pass'
    
    def get_chat_placeholder(self):
        return self.settings.chat_placeholder