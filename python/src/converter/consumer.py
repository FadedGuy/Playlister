import pika, sys, os, json
import pymongo
from utils import util

client = pymongo.MongoClient(util.get_mongo_uri())
db = client[os.environ.get('MONGO_DB')]
collection = db[os.environ.get('MONGO_USER_HISTORY_COLLECTION')]

def service(body):
    print(body, file=sys.stderr)
    jsonBody = json.loads(body)
    collection_id = jsonBody['collection_id']
    id = jsonBody['id']

    # Update status to being processed
    res = collection[collection_id].update_one(
        {"id": id},
        {"$set": {"processed": 1}}
    ) 

    # Get document with information
    doc = collection[collection_id].find_one(
            {"id": id}
            )

    valid, video_id, list_id, index = util.validate_yt_url(doc['yt_url'])
    print(f"{valid}, {video_id}, {list_id}, {index}", file=sys.stderr)

    if valid:
        if doc['retries'] > 3:
            return False
        if list_id:
            res = collection[collection_id].update_one(
                {"id": id},
                {"$set": {"processed": 2, "success": 1, "mix_id": list_id, "video_id": video_id}}
            )         
        else:
            processed = util.process_yt_id(video_id)
            if processed:
                res = collection[collection_id].update_one(
                    {"id": id},
                    {"$set": {"processed": 2, "success": 1, "video_id": video_id, "retries": doc['retries']+1}}
                ) 
            else: 
                res = collection[collection_id].update_one(
                    {"id": id},
                    {"$set": {"processed": 2, "video_id": video_id, "retries": doc['retries']+1}}
                ) 
    else:
        res = collection[collection_id].update_one(
            {"id": id},
            {"$set": {"processed": 2}}
        ) 
    
    print("------------------------\n", file=sys.stderr)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = service(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(
        queue=os.environ.get("MSG_QUEUE_IN"),
        on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)