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
    
    def _build_query(self,cols=['t.id','t.metadata.file_name'],year=2010,type='',region='',customer='',product='') -> str:
        search = ','.join(cols)
        query = rf"""SELECT {search} FROM WL_Calls t WHERE json_query(metadata, '$.report_date.date()?(@ > "{str(year)}-01-01T00:00")') IS NOT NULL"""
        if type:
            query = query + rf""" AND json_query(metadata, '$?(@.type == "{str(type)}")') IS NOT NULL"""
        if region:
            query = query + rf""" AND json_query(metadata, '$?(@.regions.region == "{str(region)}")') IS NOT NULL"""
        if customer:
            query = query + rf""" AND json_query(metadata, '$?(@.customer == "{str(customer)}")') IS NOT NULL"""
        if product:
            query = query + rf""" AND json_query(metadata, '$?(@.products.product starts with ("{str(product[0])}"))') IS NOT NULL"""
        return query
    
    def collect_data(self,name,data,content):
        try:
            metadata = json.dumps(data)
            file_data = (name,metadata,content)
            if file_data in self.main_data:
                pass
            else:
                self.main_data.append(file_data)
        except Exception as e:
            logger.debug(e)

    def update_db_records(self):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            try:
                query = "INSERT INTO WL_Calls (file_name,metadata,content) VALUES(:1,:2,:3)"
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
            year:int=2010,
            type:str=None,
            region:str=None,
            customer:str=None,
            product:str=None
        ):
        db_query = self._build_query(name_list,year,type,region,customer,product)
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
            ['t.metadata.report_date','t.metadata.type','t.metadata.regions[0].region']
        )
    print(responses)

if __name__=='__main__':
    main()