import pika, sys, os, json
import pymongo
import datetime
from utils import util
from playlisterUtil.playlisterUtil import get_mongo_uri, MongoDoc

client = pymongo.MongoClient(get_mongo_uri())
db = client[os.environ.get('MONGO_DB')]
collection = db[os.environ.get('MONGO_USER_HISTORY_COLLECTION')]

def service(body):
    print(body, file=sys.stderr)
    jsonBody = json.loads(body)
    collection_id = jsonBody['collection_id']
    id = jsonBody['id']

    doc = collection[collection_id].find_one({"id": id})
    # Error collection not found
    if not doc:
        print("No collection found!", file=sys.stderr)

    mongoDoc = MongoDoc.filter_mongo_doc(doc)
    
    # Update status to being processed
    mongoDoc.set_value('processed', 1)
    mongoDoc.set_value('startedProcessing', str(datetime.datetime.utcnow()))
    mongoDoc.set_value('retries', mongoDoc.get_value('retries')+1)
    mongoDoc.update_values_mongo(collection, collection_id)

    err = util.validate_yt_url(mongoDoc, collection, collection_id)
    if err:
        # Max retries: ack and leave it unprocessed
        if mongoDoc.get_value('retries') > 3:
            mongoDoc.set_value('processed', 2)
            mongoDoc.set_value('finishedProcessing', str(datetime.datetime.utcnow()))
            mongoDoc.update_values_mongo(collection, collection_id)
            return True
    
    err = util.process_yt_id(mongoDoc)
    if err:
        print("Error in processing", file=sys.stderr)
        mongoDoc.update_values_mongo(collection, collection_id)
        return True
    
    mongoDoc.set_value('processed', 2)
    mongoDoc.set_value('finishedProcessing', str(datetime.datetime.utcnow()))
    mongoDoc.update_values_mongo(collection, collection_id)
    print("------------------------\n", file=sys.stderr)

    return False

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

