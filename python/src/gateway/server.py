import os, gridfs, pika, json, sys
from flask import Flask, request, render_template, make_response, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from auth import validate
from auth_svc import access
from storage import util

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
    access_token = get_access_token(request)
    if not access_token:
        return "not authorized", 401

    token, err = validate.token(access_token)
    if not err:
        return "sucess!", 200   
    else:
        return "not authorized", 401

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

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


@server.route("/", methods=["GET"])
def index_page():
    access_token = get_access_token(request)
    if not access_token:
        return render_template("index.html")
    
    token, err = validate.token(access_token)
    if not err:
        return redirect(url_for("app_page"))
    else:
        return render_template("index.html")


@server.route("/app", methods=["GET"])
def app_page():
    access_token = get_access_token(request)
    if access_token is None:
        return redirect(url_for("index_page"))

    token, err = validate.token(access_token)
    if not err:
        return render_template("app.html")
    else:
        return redirect(url_for("index_page"))

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
