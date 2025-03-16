from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .api.routers import crawl

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许跨域请求
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许所有方法
    allow_headers=["*"], # 允许所有请求头
)

# 定义根路由
@app.get("/")
async def root():
    return {"message": "Hello, this is the crawler API!"}

# 定义爬虫路由
app.include_router(crawl.router, prefix="/api")


# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
