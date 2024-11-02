from datetime import datetime

import paho.mqtt.client as mqtt

class MqttObserver:
    def __init__(self, broker, port, topics):
        """
        Initialize the MqttObserver with broker, port, and topics.

        :param broker: The MQTT broker address.
        :param port: The MQTT broker port.
        :param topics: A dictionary of topics to subscribe to.
                The dictionary should have the following keys:
                - "lever_state": The topic for the lever state.
                - "door_events": The topic for the door events.
                - "spacestatus_isOpen": The topic for the space status.
                - "spacestatus_lastchange": The topic for the last change of the space status.
        """
        self.broker = broker
        self.port = int(port)
        self.topics = topics

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.door_locked = False
        self.lever_open = False


    def on_connect(self, client, _userdata, _flags, rc):
        print(f"Connected with result code {rc}")
        for key in ['lever_state', 'door_events']:
            print(f"Subscribing to topic {key}")
            client.subscribe(self.topics[key])

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with result code {rc}")
        if rc != 0:
            print("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()

    def on_message(self, client, userdata, msg):
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
        self.on_message_callback(msg.topic, msg.payload.decode())

    def on_message_callback(self, topic, message):
        if topic == self.topics["lever_state"]:
            self.handle_lever_state(message)
        elif topic == self.topics["door_events"]:
            self.handle_door_events(message)

        self.update_status()
        self.update_traffic_light()

    def handle_lever_state(self, state):
        self.lever_open = state == "open"

    def handle_door_events(self, event):
        self.door_locked = event == "door locked"

    def update_status(self):
        self.client.publish(self.topics["spacestatus_isOpen"], "true" if self.lever_open else "false")
        self.client.publish(self.topics["spacestatus_lastchange"], str(int(datetime.now().timestamp())))

    def update_traffic_light(self):
        color = "green" if self.lever_open else "red"
        cmd = color + (" blink" if self.door_locked else "")
        self.client.publish(self.topics["traffic_light"], cmd)

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()