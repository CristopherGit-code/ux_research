from src.modules.config import Settings
from src.modules.file_handler import File_handlder
from src.modules.oci_client import Client
from src.modules.db import DataBase
from pathlib import Path
import json,logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='Test_update')

source_folder = Path(r"C:\Users\Cristopher Hdz\Desktop\Test\ux_research\src\assets\Transcripts")
template = r'C:\Users\Cristopher Hdz\Desktop\Test\ux_research\src\assets\template.json'

settings = Settings('ux.yaml')
file_manager = File_handlder()
llm = Client(settings)
db = DataBase(settings)

missing = ['Lisa', 'Lyza', 'Nia', 'Nick', 'Shavorrian', 'Zenaiah']

with open(template,'r') as file:
    metadata = json.load(file)

for file_path in source_folder.iterdir():
    if file_path.is_file():
        file_suffix = str(file_path.suffix)
        file_name = str(file_path.name).replace(file_suffix,'')
        if file_name in missing:
            missing.remove(file_name)
            md = file_manager.parse_file(file_path)
            md = md.replace(" ","")
            logger.debug('Parsed data')
            prompt= f'Given the information from a report, use the template: {metadata}, fill al the required information according to the report and generate a json file using " for all the tags. Include much information as possible. The report is: {md}'
            instructions = f'Use the format and fill the required fields to generate a json file using double quotes. Use only the information given. If data not present, colocate as unknown. Return only the json format, no extra text. For date: yyyy-mm-dd. Format to fill: {metadata}'
            response = llm._call_client(prompt,instructions)
            prompt = f'Analyse the following text: {response}. The text is a JSON format but incomplete or with errors, fix the sintax from the format accoring to the template: {metadata}, using correcly double quotes and commas. Do not add extra fields or information. If the format is correct, do not modify and return the same format just as given. If the text is not similar to a JSON format, rather a natural response, try to build the JSON format according to the template.'
            response = llm.answer_prompt(prompt,"Ensure the JSON formatting is as accurate as possible, concentrate on building a correct JSON format to be read")
            verify,data = file_manager.verify_json(response)
            if verify:
                db.collect_data(file_name,data,md)
                new_file_name = file_name + '.json'
                profile = rf'C:/Users/Cristopher Hdz/Desktop/Test/ux_research/src/assets/json/{new_file_name}'
                with open(profile,'w',encoding='utf-8') as file:
                    file.write(response)
                logger.info(f'File written: {file_name}')
            else:
                missing.append(file_name)
                logger.debug(f'JSON response in wrong format for file: {file_name}')
        else:
            pass

print(f'Files converted.\nMissing files:\n{missing}\n')
# db._init()
db.update_db_records()