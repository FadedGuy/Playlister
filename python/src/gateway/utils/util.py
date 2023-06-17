import os, pika, json, datetime
from base64 import b64encode

def get_mongo_uri() -> str :
    return f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASS')}@{os.environ.get('MONGO_SVC_ADDRESS')}/{os.environ.get('MONGO_DB')}" 


def get_collection_id(token) -> str:
    username = json.loads(token)['username'].encode()
    return b64encode(username).decode()


def get_docs_cursor(collection, token, filter={}):
    collection_id = get_collection_id(token)
    return collection[collection_id].find(filter)


def add_url_db(collection, token, url):
    collection_id = get_collection_id(token)
    n_id = collection[collection_id].count_documents({})
    # If already in collection same url dont add
    collection[collection_id].insert_one({
        'yt_url': url,
        'yt_title': "",
        'dateInit': str(datetime.datetime.utcnow()),
        'id': n_id,
        'spotify_url': "",
        'spotify_preview': "",
        # 0 not processed, 1 in process, 2 processed
        'processed': 0,
        'success': 0,
        'mix_id': "",
        'video_id': "",
        # Type of video
        'type': 4,
        'retries': 0
        })

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