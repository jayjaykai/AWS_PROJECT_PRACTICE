from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import boto3
from model.dbconfig import db 

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
load_dotenv()

# 設定可存取資源的來源端點
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有HTTP方法
    allow_headers=["*"],  # 允許所有HTTP headers
)


@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")

@app.get("/api/msg")
async def getmsg() :
    con, cursor = db.connect_mysql_server()
    if cursor is not None:
        try:
            Result = []
            cursor.execute("select content, pic_url from msg order by time desc")
            val = cursor.fetchall()
            for i in range(len(val)):
                msg = val[i][0]
                pic_key = val[i][1]
                Result.append([msg, pic_key])              
        except Exception as err:
            print(f"Error updating order: {err}")
            return JSONResponse(status_code=400, content={"error": True, "message": "取得資料庫資料失敗"})
        finally:
            con.close()
        return JSONResponse(status_code=200, content={"success": True, "data": Result})
    
@app.post("/api/msg")
async def upload(file: UploadFile = File(...), content: str = Form(...)):
    # 加載環境變數中的AWS憑證
    S3_BUCKET = os.getenv('S3_BUCKET')
    REGION = os.getenv('AWS_REGION')
    CLOUDFRONT = os.getenv('CLOUDFRONT')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        return JSONResponse(status_code=500, content={"error": True, "message": "AWS credentials not found in environment variables"})

    s3_client = boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
  
    try:
        file_name = file.filename
        file_content = await file.read()

        # 上傳圖片到S3
        s3_client.put_object(Bucket=S3_BUCKET, Key=file_name, Body=file_content)
        print(f"{file_name} uploaded to S3.")

        con, cursor = db.connect_mysql_server()
        if cursor is not None:
            try:
                cursor.execute("INSERT INTO msg(content, pic_url) VALUES(%s, %s)", (content, CLOUDFRONT + file_name))
                con.commit()

            except Exception as err:
                print(f"Error inserting message: {err}")
                return JSONResponse(status_code=400, content={"error": True, "message": "Failed to insert message into database"})
            finally:
                con.close()
        return JSONResponse(status_code=200, content={"success": True, "message": "Photo uploaded successfully!"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": "Internal server error"})