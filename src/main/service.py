import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imports import *

APIKey_Header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verifyAPIKey(APIKey: str = Depends(APIKey_Header)):
    if Config.STOCKS_API['KEY.SYSTEM'] == 'FALSE':
        return None
    
    validKey = Config.STOCKS_API.get('KEY')
    if not validKey:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    if APIKey is None or APIKey != validKey:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    return APIKey

class Service:
    instances = {}
    
    def __init__(self, service_name: str, port: int):
        self.service_name = service_name
        self.port = int(port)
        self.app = FastAPI(title=service_name, version="1.0.0")
        self.setupRoutes()
    
    def setupRoutes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "service": self.service_name, "port": self.port, "timestamp": str(time.time())}
        
        @self.app.get("/")
        async def root():
            return {"message": "Mansa (Stocks API)"}
        
        @self.app.get("/api/key")
        async def APIKeyTest(api_key: str = Depends(verifyAPIKey)):
            return {"message": "API", "secured": True}
        
        @self.app.get("/api/historical")
        async def getHistorical(search: str = Query(...), fields: str = Query(...), years: str = Query(...), api_key: str = Depends(verifyAPIKey)):
            return await self.queryHistorical(search, fields, years)
        
        @self.app.get("/api/fundamental")
        async def getFundamental(search: str = Query(...), fields: str = Query(...), dates: str = Query(...), api_key: str = Depends(verifyAPIKey)):
            return await self.queryFundamental(search, fields, dates)
    
    def parseDateRange(self, date_str: str, is_single: bool = True) -> tuple:
        """Parse date string and return (start_date, end_date)"""
        if len(date_str) == 4:  # Year only
            return f"{date_str}-01-01", f"{date_str}-12-31"
        elif len(date_str) == 7:  # Year-Month
            year, month = int(date_str[:4]), int(date_str[5:7])
            last_day = pd.Timestamp(year=year, month=month, day=1).days_in_month
            return f"{date_str}-01", f"{date_str}-{last_day:02d}"
        return date_str, date_str
    
    def buildQuery(self, search: str, fields: list, date_start: str, date_end: str, query_type: str) -> tuple:
        """Build SQL query based on type (fundamental or historical)"""
        cols = ["`TICKER`", "`NOME`"]
        
        if query_type == "fundamental":
            cols.insert(2, "`TIME`")
            cols.extend([f"`{field}`" for field in fields])
        else:
            cols.extend([f"`{field} {year}`" for field in fields for year in range(int(date_start), int(date_end) + 1)])
        
        where_clause = "(UPPER(`TICKER`) = UPPER(:search) OR UPPER(`NOME`) LIKE CONCAT('%', UPPER(:search), '%'))"
        
        if query_type == "fundamental":
            where_clause += " AND DATE(`TIME`) BETWEEN DATE(:date_start) AND DATE(:date_end)"
        
        query = text(f"SELECT {', '.join(cols)} FROM b3_stocks WHERE {where_clause} ORDER BY `TIME` DESC LIMIT 1000")
        
        return query, {"search": search, "date_start": date_start, "date_end": date_end}
    
    async def queryHistorical(self, search: str, fields: str, years: str):
        try:
            field_list = [f.strip() for f in fields.split(",")]
            year_list = [int(y.strip()) for y in years.split(",")]
            
            if len(year_list) == 1:
                year_start = year_end = year_list[0]
            elif len(year_list) == 2:
                year_start, year_end = year_list
            else:
                raise HTTPException(status_code=400, detail="Years format: YEAR or START_YEAR,END_YEAR")
            
            query, params = self.buildQuery(search, field_list, str(year_start), str(year_end), "historical")
            df = self.executeQuery(query, params)
            
            if df.empty:
                raise HTTPException(status_code=404, detail=f"No data found for: {search}")
            
            return {"search": search, "fields": field_list, "years": [year_start, year_end], "type": "historical", "data": json.loads(df.to_json(orient="records"))}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")
    
    async def queryFundamental(self, search: str, fields: str, dates: str):
        try:
            field_list = [f.strip() for f in fields.split(",")]
            date_list = [d.strip() for d in dates.split(",")]
            
            if len(date_list) == 1:
                actual_start, actual_end = self.parseDateRange(date_list[0], is_single=True)
                original_date = date_list[0]
            elif len(date_list) == 2:
                actual_start, actual_end = date_list[0], date_list[1]
                original_date = date_list[0]
            else:
                raise HTTPException(status_code=400, detail="Dates format: DATE or START_DATE,END_DATE")
            
            query, params = self.buildQuery(search, field_list, actual_start, actual_end, "fundamental")
            params["date_start"], params["date_end"] = actual_start, actual_end
            
            df = self.executeQuery(query, params)
            
            if df.empty:
                raise HTTPException(status_code=404, detail=f"No data found for: {search}")
            
            if 'TIME' in df.columns:
                df['TIME'] = pd.to_datetime(df['TIME']).astype(str)
            
            return {"search": search, "fields": field_list, "dates": [original_date, date_list[1] if len(date_list) == 2 else original_date], "type": "fundamental", "data": json.loads(df.to_json(orient="records"))}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching fundamental data: {str(e)}")
    
    def executeQuery(self, query: str, params: dict) -> pd.DataFrame:
        engine = create_engine(f"mysql+pymysql://{Config.MYSQL['USER']}:{Config.MYSQL['PASSWORD']}@{Config.MYSQL['HOST']}/{Config.MYSQL['DATABASE']}")
        with engine.connect() as connection:
            result = connection.execute(query, params)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    
    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="critical")
    
    @classmethod
    def initialize(cls, service_name: str, port: int):
        key = f"{service_name}_{port}"
        if key not in cls.instances:
            instance = cls(service_name, port)
            thread = threading.Thread(target=instance.run, daemon=True)
            thread.start()
            cls.instances[key] = instance
        return cls.instances[key]