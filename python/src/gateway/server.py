import os, pika, json, sys
from flask import Flask, request, make_response, jsonify
import pymongo
from flask_cors import CORS
from auth import verify
from auth_svc import access
from utils import util

server = Flask(__name__)

CORS(server, supports_credentials=True)

client = pymongo.MongoClient(util.get_mongo_uri())
db = client[os.environ.get('MONGO_DB')]
collection = db[os.environ.get('MONGO_USER_HISTORY_COLLECTION')]

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

def get_access_token(request):
    return request.cookies.get(os.environ.get('ACCESS_TOKEN_ID'))

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if not err:
        return jsonify({os.environ.get('ACCESS_TOKEN_ID'): token}), 200
        # Soy consciente que esta no es la manera, pero, que esperan de mi llevo 3 dias y esto no funciona
        # response = make_response()
        # response.set_cookie(os.environ.get('ACCESS_TOKEN_ID'), token, httponly=False, secure=False, path='/')
        # return response
    else:
        return err
    
@server.route("/validate", methods=["POST"])
def validate():
    # get_access_token instead of that when https
    access_token = request.headers.get('Authorization')
    if not access_token:
        return "not authorized", 401

    token, err = verify.token(access_token)
    if not err:
        return "success", 200   
    else:
        return "not authorized", 401


@server.route("/sendURL", methods=["POST"])
def sendURL():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return "not authorized", 401
    
    token, err = verify.token(access_token)
    if not err:
        try:
            youtubeURL = request.get_data(as_text=True)
            message = util.add_url_db(collection, token, youtubeURL)
            print("Added", file=sys.stderr)

            # If fail, delete doc added to db
            util.send_url_queue(channel, os.environ.get("MSG_QUEUE_IN"), message)
            print("Sent", file=sys.stderr)

            return "sucess", 200
        except Exception as err:
            print(err, file=sys.stderr)
            return "internal server error", 500
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return "not authorized", 401
    
    token, err = verify.token(access_token)
    if not err:
        try:
            cursor = util.get_docs_cursor(collection, token)
        except Exception as err:
            print(err, file=sys.stderr)
            return "internal server error", 500

        jsonResponse = []
        for doc in cursor:
            # Filter unwanted elements the client shouln't have like _id
            jsonResponse.append({
                'yt_url': doc['yt_url'],
                'dateInit': doc['dateInit'],
                'id': doc['id'],
                'spotify_url': doc['spotify_url'],
                })
        
        print(jsonResponse, file=sys.stderr)

        return jsonResponse, 200
    else:
        return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
