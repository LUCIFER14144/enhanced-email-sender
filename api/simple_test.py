from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def test():
    return {"message": "Simple test working", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "test": "working"}

# For Vercel
def handler(request):
    return app(request)