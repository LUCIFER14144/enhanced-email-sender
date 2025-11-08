"""
Download handler for Enhanced Email Sender
Serves files from GitHub without exposing the source
"""
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse, StreamingResponse
import httpx

app = FastAPI()

# GitHub raw file URLs (internal only)
GITHUB_BASE = "https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/dist/"

FILES = {
    "exe": {
        "url": f"{GITHUB_BASE}Enhanced-Email-Sender.exe",
        "filename": "Enhanced-Email-Sender.exe",
        "content_type": "application/octet-stream"
    },
    "zip": {
        "url": f"{GITHUB_BASE}Enhanced-Email-Sender.zip",
        "filename": "Enhanced-Email-Sender.zip",
        "content_type": "application/zip"
    }
}


@app.get("/api/download/exe")
async def download_exe():
    """Download the EXE file"""
    file_info = FILES["exe"]
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(file_info["url"])
        
        if response.status_code == 200:
            return Response(
                content=response.content,
                media_type=file_info["content_type"],
                headers={
                    "Content-Disposition": f'attachment; filename="{file_info["filename"]}"',
                    "Cache-Control": "no-store"
                }
            )
        else:
            return Response(
                content="File not found",
                status_code=404
            )


@app.get("/api/download/zip")
async def download_zip():
    """Download the ZIP file"""
    file_info = FILES["zip"]
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(file_info["url"])
        
        if response.status_code == 200:
            return Response(
                content=response.content,
                media_type=file_info["content_type"],
                headers={
                    "Content-Disposition": f'attachment; filename="{file_info["filename"]}"',
                    "Cache-Control": "no-store"
                }
            )
        else:
            return Response(
                content="File not found",
                status_code=404
            )
