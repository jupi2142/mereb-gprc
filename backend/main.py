import os

import uvicorn
from dotenv import load_dotenv
from gateway import app

load_dotenv()


def main():
    print("Hello from mereb-gprc!")
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
