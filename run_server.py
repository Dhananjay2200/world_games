"""
WorldGames AI - Server Launcher.
Runs FastAPI on the configured host and port (default: 8001).
"""

import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    print("=" * 65)
    print(f" Starting {settings.APP_NAME} Backend")
    print(f" Server URL: http://{settings.HOST}:{settings.PORT}")
    print(f" Swagger Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f" Admin Credentials: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
    print("=" * 65)
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
