#!/usr/bin/python

# Script to poll the UPS (via apcupsd) and publish interesting facts to
# MQTT.

# Originally published under GPL3+ by Andrew Elwell <Andrew.Elwell@gmail.com>
# Updated for use with paho by boneless <bonelessc@gmail.com>

import subprocess
# we use paho mosquitto for the MQTT part
import paho.mqtt.client as mqtt

# which status messages to publish. We use upsname as part of the topic
interesting = ("status", "linev", "loadpct", "battv", "bcharge", "timeleft", "tonbatt")
apc_status = {}

host = "10.0.0.0"
user = "user"
pw = "pw"
topic = "topic"

res = subprocess.check_output("/sbin/apcaccess")

for line in res.split("\n"):
    (key,spl,val) = line.partition(": ")
    key = key.rstrip().lower()
    val = (val.strip()).partition(" ")[0]
    apc_status[key] = val

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
        print("Published")

def on_subscribe(mid, granted_qos):
        print "Subscribed:",mid,granted_qos

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.username_pw_set(user, pw)
mqttc.connect(host, 1883, 60)

for thing in interesting:
    mqttc.publish(topic+"/%s/%s" % (apc_status["upsname"],thing), apc_status[thing])