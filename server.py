from fastapi import FastAPI, File, Form

from SqliteHelper import *
from localtime import *
import config

app = FastAPI() #создание экземпляра FastAPI


@app.on_event("startup")
def DB_init():
    global helper
    helper = SqliteHelper(config.DB_filename)


@app.post("/send")
async def send(
                file_date: bytes = File(...),
                symbols_plate: str = Form(...),
                region: int = Form(...),
                type: str = Form(...)
                ):
    
    input_data = (type, symbols_plate, region, get_unixtime(), file_date)
    helper.insert("INSERT INTO license_plates (type, symbols_plate, region, date, media) VALUES(?,?,?,?,?)", input_data)
    
    return {
            "symbols_plate": symbols_plate,
            "region": region,
            "type": type
            }   

    
@app.get("/")
async def root():
    return {"message": "Hello World!"}