import paho.mqtt.client as mqtt
import ssl
import couchdb
import json

DELIMITER = ";;;;"

# print(data['iotWatchdogUUID'])
# s = json.dumps(data, indent=4, sort_keys=True)
# print(s)
def validatePayload(payload):
    tmpPayload = payload.decode('utf8').replace("'", '"').replace("\n", "")
    jsonPayload = json.loads(tmpPayload)

    if not 'iotWatchdogUUID' in jsonPayload:
        print('Invalid payload!')

        return None

    return jsonPayload

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("/cit/msc/iot/watchdog/#")

def makeDeviceDataAsJsonList(deviceData):
    header = deviceData[0]
    keys = header.split(DELIMITER)

    deviceDataAsJsonList = []

    index = 1
    while index < len(deviceData):
        line = deviceData[index]
        values = line.split(DELIMITER)

        if len(keys) == len(values):
            object = {}

            for position in range (0, len(values)):
                object[keys[position]] = values[position]

                deviceDataAsJsonList.append(object)

        index += 1

    return deviceDataAsJsonList

def formatRunningProcesses(payload):
    runningProcesses = {}

    runningProcesses['iotWatchdogUUID'] = payload['iotWatchdogUUID']
    runningProcesses['executionTime'] = payload['executionTime']
    runningProcesses['memoryProcesses'] = makeDeviceDataAsJsonList(payload['memoryProcesses'])

    return runningProcesses

def formatNetworkTraffic(payload):
    networkTraffic = {}

    networkTraffic['iotWatchdogUUID'] = payload['iotWatchdogUUID']
    networkTraffic['executionTime'] = payload['executionTime']
    networkTraffic['networkTraffic'] = makeDeviceDataAsJsonList(payload['networkTraffic'])

    return networkTraffic

def on_message(client, userdata, msg):
    jsonPayload = validatePayload(msg.payload)

    if jsonPayload != None:
        if str(msg.topic).endswith("registration"):
            print("Registration")

            db = couch['registration-db']
            db.save(jsonPayload)
        elif str(msg.topic).endswith("reboot"):
            print("Reboot")

            db = couch['reboot-db']
            db.save(jsonPayload)
        elif str(msg.topic).endswith("device"):
            print("Device Data")

            runningProcesses = formatRunningProcesses(jsonPayload)
            db = couch['running-processes-db']
            db.save(runningProcesses)

            networkTraffic = formatNetworkTraffic(jsonPayload)
            db = couch['network-traffic-db']
            db.save(networkTraffic)
        else:
            print("Error")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set("cert/server.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect("dissertation-server", 8883, 60)

# client.tls_set("cert/mosquitto.org.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
# client.connect("test.mosquitto.org", 8883, 60)

couch = couchdb.Server('http://dissertation-server:5984/')

client.loop_forever()
