import uvicorn
from api import app
from shared import CONFIG
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=CONFIG['server_ip'],
        port=int(CONFIG['server_port']),
        reload=False,
    )
