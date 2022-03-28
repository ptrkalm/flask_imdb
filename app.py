from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)

from routes import *

app.run()

