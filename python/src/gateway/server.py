import os, gridfs, pika, json, sys
from flask import Flask, request, make_response, jsonify
import pymongo
from flask_cors import CORS
from auth import verify
from auth_svc import access

server = Flask(__name__)

# server.config["MONGO_URI"] = "mongodb://mongo:27017/database"

CORS(server, supports_credentials=True)

# mongo = PyMongo(server)
uri = "mongodb://" + os.environ.get("MONGO_USER") + ":" + os.environ.get("MONGO_PASS") + "@" + os.environ.get("MONGO_SVC_ADDRESS") + "/database" 
client = pymongo.MongoClient("mongodb://gatewayUser:gatewayPassword@mongo:27017/database")
db = client["database"]
# fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
# channel = connection.channel()

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
def sendMessage():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return "not authorized", 401
    
    token, err = verify.token(access_token)
    if not err:
        try:
            message = request.get_data(as_text=True)

            connection.channel().basic_publish(
                exchange="",
                routing_key="msg",
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

            return "sucess", 200
        except Exception as err:
            return "internal server error", 500
    else:
        return "not authorized", 401

@server.route("/download", methods=["GET"])
def download():
    print(db.list_collections(), file=sys.stderr)
    return "sucess", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
