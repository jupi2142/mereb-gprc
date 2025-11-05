import uvicorn
from gateway import app

def main():
    print("Hello from mereb-gprc!")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
