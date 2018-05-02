import paho.mqtt.client as mqtt
import ssl

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("/cit/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set("server.crt", tls_version=ssl.PROTOCOL_TLSv1_2)

client.connect("192.168.56.101", 8883, 60)

client.loop_forever()
