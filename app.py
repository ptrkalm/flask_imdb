from dotenv import load_dotenv
from flask import Flask
from routes import app

load_dotenv()
app.run()

