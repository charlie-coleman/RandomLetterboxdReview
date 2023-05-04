import flask
from flask_cors import CORS, cross_origin
import uuid
from pathlib import Path
import pytz
import json
import argparse
import datetime as dt
from letterboxdrss import *

class DataStore():
  lbxddata : LetterboxdRSS = None

data = DataStore()

app = flask.Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = 'Content-Type'
  
@app.route('/api/v1/random', methods=['GET'])
@cross_origin()
def random_review():
  return data.lbxddata.get_random_review()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--host', '-i', default="127.0.0.1", help="API Host IP")
  parser.add_argument('--port', '-p', type=int, default=8080, help="API Port")
  parser.add_argument('--letterboxd', '-l', type=str, default='itswill', help="Letterboxd ID to get RSS reviews from.")
  
  args = parser.parse_args()
  
  data.lbxddata = LetterboxdRSS(args.letterboxd, './data/reviews.csv')
  
  app.run(host=args.host, port=args.port, debug=True)
