from markitdown import MarkItDown
import logging,json
from pathlib import Path

logger = logging.getLogger(name=f'File.{__name__}----------->')

class File_handlder():
    def __init__(self):
        self.md = MarkItDown()
        self.source_folder = Path(r'C:\Users\Cristopher Hdz\Desktop\Test\WordAnalizer\Files\Call reports')

    def parse_file(self, file) -> str:
        result = self.md.convert(file)
        return result.text_content
    
    def verify_json(self,json_data):
        try:
            metadata = json.loads(json_data)
            return True,metadata
        except Exception as e:
            logger.debug(e)
            return False,[]
        
    def merge_md(self,file_list):
        info_pack = ''
        for data in file_list:
            info_pack = info_pack + '\n' + data
        return info_pack

    # Local functions TESTING
    def store_file(self,text,file_name):
        file_name = file_name + '.md'
        file_path = rf'C:/Users/Cristopher Hdz/Desktop/Test/WordAnalizer/Files/md/{file_name}'
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)

    def get_files_folder(self):
        for file_path in self.source_folder.iterdir():
            if file_path.is_file():
                file_name = str(file_path.name).replace('.docx','')
                mrkdwn = self.parse_file(file_path)
                self.store_file(mrkdwn,file_name)

def main():
    file_handler = File_handlder()
    file_handler.get_files_folder()

if __name__ == '__main__':
    main()