import os, pika, json, datetime, sys
from base64 import b64encode
from playlisterUtil.playlisterUtil import MongoDoc

def get_collection_id(token) -> str:
    username = json.loads(token)['username'].encode()
    return b64encode(username).decode()

def get_docs_cursor(collection, token, filter={}):
    collection_id = get_collection_id(token)
    return collection[collection_id].find(filter)


def add_url_db(collection, token, url):
    collection_id = get_collection_id(token)
    n_id = collection[collection_id].count_documents({})

    doc = MongoDoc()
    doc.set_value('youtube.url', url)
    doc.set_value('createdAt', str(datetime.datetime.utcnow()))
    doc.set_value('id', n_id)
    doc.insert_one_mongo(collection, collection_id)
    # If already in collection same url dont add
    
    return json.dumps({"id": n_id, "collection_id": collection_id})


def send_url_queue(key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", heartbeat=600, blocked_connection_timeout=300))
    channel = connection.channel()

    channel.basic_publish(
        exchange="",
        routing_key=key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
    )

    channel.close()