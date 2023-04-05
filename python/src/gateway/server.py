import os, gridfs, pika, json, sys
from flask import Flask, request, make_response, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from auth import verify
from auth_svc import access

server = Flask(__name__)

server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"
CORS(server, supports_credentials=True)

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

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
    print(err, file=sys.stderr)
    if not err:
        return "success", 200   
    else:
        return "not authorized", 401

@server.route("/upload", methods=["POST"])
def upload():
    access, err = verify.token(request)

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) != 1:
            return "exactly 1 file required", 400
        
        for _, f in request.files.items():
            print("ye")
            # err = util.upload(f, fs, channel, access)
            if err:
                return err
    
        return "sucess!", 200
    else:
        return "not authorized", 401
    
@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
