import os
from dotenv import load_dotenv
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json

load_dotenv()
END_POINT = os.getenv('END_POINT')
PATH_CERT = os.getenv('PATH_CERT')
PATH_PRI_KEY = os.getenv('PATH_PRI_KEY')

# ------------------------------- Callback Definitions ------------------------------- #
# Note: on_message_received() is defined outside the class by the user.

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)



def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

def do_nothing_on_message_received(topic, payload, dup, qos, retain, **kwargs):
    pass

class _MQTT_conn:
    # -------------------------------------- init -------------------------------------- #
    def __init__(self, client_ID, on_message_received):

        # Create a MQTT connection from the command line data
        self.conn = mqtt_connection_builder.mtls_from_path(
            endpoint=END_POINT,
            port=8883,
            cert_filepath=PATH_CERT,          # path to [thing].cert.pem
            pri_key_filepath=PATH_PRI_KEY,    # path to [thing].private.key
            ca_filepath=None,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=client_ID,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None,
            on_connection_success=on_connection_success,
            on_connection_failure=on_connection_failure,
            on_connection_closed=on_connection_closed)

        print("Connecting to endpoint: with client ID: {}".format(client_ID))
        conn_future = self.conn.connect()


        # Future.result() waits until a result is available
        conn_future.result()
        print("Connected!")

        self.on_message_received = on_message_received
        self.subscriptions = []

    # ------------------------ subscribe, publish and disconnect ------------------------ #
    def subscribe(self, message_topic):
        print("Subscribing to topic '{}'...".format(message_topic))
        subscribe_future, packet_id = self.conn.subscribe(
            topic=message_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))
        self.subscriptions.append(message_topic)

    def publish(self, message_topic, message):
        print("Publishing message to topic '{}': {}".format(message_topic, message))
        message_json = json.dumps(message)
        self.conn.publish(
            topic=message_topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)

    def disconnect(self):
        print("Disconnecting...")
        disconnect_future = self.conn.disconnect()
        disconnect_future.result()
        print("Disconnected!")


received_count = 0
received_all_event = threading.Event()

# Callback when the subscribed topic receives a message
# defined outside the class!
# note the args!!!!!!!
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == 10:
       received_all_event.set()


if __name__ == '__main__':
    _mqtt = _MQTT_conn("test-123", on_message_received)
    # _mqtt.subscribe("test/topic")
    # _mqtt.publish("test/topic", "my own hello world")
    # while(received_count == 0):
    #     pass
    _mqtt.disconnect()
