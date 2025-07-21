import oracledb,json,logging
from .config import Settings

logger = logging.getLogger(name='DB details')

class DataBase:
    def __init__(self, settings: Settings):
        self._settings = settings

        db_params = self._settings.database
        assert db_params
        self._pool = oracledb.ConnectionPool(
            config_dir=db_params['walletPath'],
            user=db_params['username'],
            password=db_params['DB_password'],
            dsn=db_params['dsn'],
            wallet_location=db_params['walletPath'],
            wallet_password=db_params['walletPass'],
            min=2,
            max=10,
            increment=1,
        )
    
        self.main_data = []
        logger.info('---------- DB Pool created ----------')

    def _get_connection(self):
        logger.info('Connected to DB')
        return self._pool.acquire()
    
    def _build_query(self,cols=['t.id','t.metadata.study'],study='',location='US',utility='',property_type='',characteristics='',products='',events='') -> str:
        search = ','.join(cols)
        query = rf"""SELECT {search} FROM UX_Research t WHERE json_query(metadata, '$?(@.regions.region == "{str(location)}")') IS NOT NULL"""
        return query
        if utility:
            query = query + rf""" AND json_query(metadata, '$?(@.type == "{str(type)}")') IS NOT NULL"""
        if property_type:
            query = query + rf""" AND json_query(metadata, '$?(@.regions.region == "{str(region)}")') IS NOT NULL"""
        if characteristics:
            query = query + rf""" AND json_query(metadata, '$?(@.customer == "{str(customer)}")') IS NOT NULL"""
        if products:
            query = query + rf""" AND json_query(metadata, '$?(@.products.product starts with ("{str(product[0])}"))') IS NOT NULL"""
    
    def collect_data(self,name,data,content):
        try:
            metadata = json.dumps(data)
            file_data = (name,metadata)
            if file_data in self.main_data:
                pass
            else:
                self.main_data.append(file_data)
        except Exception as e:
            logger.debug(e)

    def update_db_records(self):
        logger.debug(self.main_data)
        with self._get_connection() as connection:
            cursor = connection.cursor()
            try:
                query = "INSERT INTO UX_Research (file_name,metadata) VALUES(:1,:2)"
                cursor.executemany(query,self.main_data)
                connection.commit()
                logger.info('rows inserted')
            except Exception as e:
                logger.debug(e)

    def _sort_files(self,query:str) -> list:
        db_responses = []
        with self._get_connection() as connection:
            cursor = connection.cursor()
            rows = cursor.execute(query)
            for row in rows:
                db_responses.append(row)
        return db_responses
    
    def get_db_response(
            self,
            name_list,
            study:str=None,
            location:str="US",
            utility:str=None,
            property_type:str=None,
            characteristics:str=None,
            products:str=None,
            events:str=None
        ):
        db_query = self._build_query(name_list,study,location,utility,property_type,characteristics,products,events)
        db_response = self._sort_files(db_query)
        lists = [list(group) for group in zip(*db_response)]
        return lists

    def _init(self):
        with self._get_connection() as connection:
            cursor = connection.cursor()

            logger.info('Started new DB table')
            
            #Drop the table 
            cursor.execute("""
                BEGIN
                    execute immediate 'drop table UX_Research';
                    exception when others then if sqlcode <> -942 then raise; end if;
                END;""")
            #Create new table
            cursor.execute("""
                CREATE TABLE UX_Research (
                    id number generated always as identity,
                    creation_ts timestamp with time zone default current_timestamp,
                    file_name varchar2(4000),
                    metadata json,
                    content VARCHAR2(32767),
                    PRIMARY KEY (id))""")

            connection.commit()
            logger.info('Table created with name: UX_Research')

def main():
    settings = Settings('ux.yaml')
    db = DataBase(settings)
    responses = db.get_db_response(
            ['t.metadata.study','t.metadata.regions[0].region','t.metadata.utility','t.metadata.property_type']
        )
    print(responses)

if __name__=='__main__':
    main()