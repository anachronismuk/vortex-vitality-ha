import requests
from paho.mqtt import client as mqtt_client
import random
import time
import json
import os
import datetime

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_DELAY = 60
CODES = {
	"N010":"🚩 Scheduled watering",
	"N011":"🚩 Poor soil drainage",
	"N012":"🚩 Not enough water",
	"N013":"🚩 Blocked pot drainage",
	"N020":"🚩 Insufficient sunlight",
	"N021":"🚩 Too much sunlight",
	"N030":"🚩 Critically LOW air temperature",
	"N031":"🚩 Critically HIGH air temperature",
	"N040":"🚩 Relative humidity is LOW",
	"N041":"🚩 Relative humidity is HIGH",
	"N070":"🚩 Late watering",
	"N201":"⚠️ 3-level sensor not fully inserted",
	"N210":"⚠️ Low moisture level",
	"N211":"⚠️ High moisture level",
	"N220":"⚠️ Insufficient sunlight",
	"N221":"⚠️ Excessive sunlight exposure",
	"N230":"⚠️ Low temperature",
	"N231":"⚠️ High temperature",
	"N240":"⚠️ Humidity is low",
	"N241":"⚠️ Humidity is high",
	"N246":"⚠️ 100% humidity warning",
	"N301":"👋 Setup is complete",
	"N340":"📷 Submit plant photo",
	"N350":"📝 Advisory Report is available",
	"N410":"🔔🍀 Health is good",
	"N411":"🔔🍀 Health is good, reminder",
	"N700":"❌ Sensor not connected",
	"N710":"🌐❌ Vprobe is OFFLINE",
	"N711":"❌ No response from Vprobe",
	"N800":"⌛ Evaluating…",
	"N810":"⌛ Identification in progress…",
	"N811":"✅ Identification complete"
}

def connect_mqtt(client_id,broker,port,username,password):
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logger("Connected to MQTT Broker!")
        else:
            logger("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_disconnect(client, userdata, rc):
    logger(f"Disconnected with result code: {rc}")
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while True:
        logger(f"Reconnecting in {reconnect_delay} seconds...")
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logger("Reconnected successfully!")
            return
        except Exception as err:
            logger("{err}. Reconnect failed. Retrying...")

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1

def publish(client,topic,msg):
  status=1
  retries=1
  while status==1 and retries<4:
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        logger(f"Attempt {retries}: Failed to send message to topic {topic}")
        retries+=1

def logger(message):
  print(f"{datetime.datetime.now().isoformat()}: {message}")

def create_vortex(client,data):
	sn=f"vplant_sn{str(data['sn']).zfill(8)}"
	device={
		"dev": {
			"ids": sn,
			"name": sn,
			"mf": "Vortex Vitality",
			"mdl": "",
			"sw": f"{data['rev']}",
			"hw": "",
			"sn": sn
			},
		"o": {
			"name": "vortex",
			"sw": "0.1",
			"url": "http://www.anachronism.co.uk"
		},
		"cmps": {
			"temperature": {
				"p": "sensor",
				"name":"Temperature",
				"device_class":"temperature",
				"unit_of_measurement":"°C",
				"value_template":"{{ value_json.tmp }}",
				"unique_id": sn+"_temperature"
			},
			"humidity": {
				"p": "sensor",
				"name":"Humidity",
				"device_class":"humidity",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.hum }}",
				"unique_id": sn+"_humidity"
			},
			"battery": {
				"p": "sensor",
				"name": "Battery",
				"device_class": "battery",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.batt }}",
				"unique_id": sn+"_battery"
			},
			"moisture": {
				"p": "sensor",
				"name": "Moisture",
				"device_class": "moisture",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.moisture }}",
				"unique_id": sn+"_moisture"
			},
			"ms1": {
				"p": "sensor",
				"name": "ms1",
				"device_class": "moisture",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.ms1 }}",
				"unique_id": sn+"_ms1"
			},
			"ms2": {
				"p": "sensor",
				"name": "ms2",
				"device_class": "moisture",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.ms2 }}",
				"unique_id": sn+"_ms2"
			},
			"ms3": {
				"p": "sensor",
				"name": "ms3",
				"device_class": "moisture",
				"unit_of_measurement":"%",
				"value_template":"{{ value_json.ms3 }}",
				"unique_id": sn+"_ms3"
			},
			"sensor count": {
				"p": "sensor",
				"state_class":"measurement",
				"value_template":"{{ value_json.mSnrs }}",
				"unique_id": sn+"_sensor_count",
				"name":"Sensor Count"
			},
			"rssi": {
				"p": "sensor",
				"name":"Signal Strength",
				"device_class": "signal_strength",
				"unit_of_measurement":"dBm",
				"value_template":"{{ value_json.rssi }}",
				"unique_id": sn+"_signal_strength"
			},
			"light": {
				"p": "sensor",
				"name":"Illuminance",
				"device_class": "illuminance",
				"value_template":"{{ value_json.light }}",
				"unit_of_measurement":"lx",
				"unique_id": sn+"_illuminance"
			},
			"time": {
				"p":"sensor",
				"name": "Timestamp",
				"device_class":"timestamp",
				"value_template":"{{ as_datetime(value_json.ts) }}",
				"unique_id": sn+"_timestamp"
			},
			"lightInd": {
				"p": "sensor",
				"name":"Light Indicator",
				"value_template": "{% if value_json.lightInd == 0 %}OK{% else %}Not OK{% endif %}",
				"unique_id": sn+"_light_indicator"
			},
			"tempInd": {
				"p": "sensor",
				"name":"Temperature Indicator",
				"value_template": "{% if value_json.tempInd == 0 %}OK{% else %}Not OK{% endif %}",
				"unique_id": sn+"temperature_indicator"
			},
			"humInd": {
				"p": "sensor",
				"name":"Humidity Indicator",
				"value_template": "{% if value_json.humInd == 0 %}OK{% else %}Not OK{% endif %}",
				"unique_id": sn+"_humidity_indicator"
			},
			"moistureInd": {
				"p": "sensor",
				"name":"Moisture Indicator",
				"value_template": "{% if value_json.moistureInd == 0 %}OK{% else %}Not OK{% endif %}",
				"unique_id": sn+"_moisture_indicator"
			},
			"message": {
				"p": "sensor",
				"name":"Message",
				"unique_id": sn+"_message",
				"state_topic": sn+"/state/message"
			}
		},
		"state_topic": sn+"/state",
		"qos":2
	}

	publish(client, "homeassistant/device/"+sn+"/config", json.dumps(device).encode("utf-8"))

def battery_calc(volt):
	if volt>2.8:
		percentage=100
	elif volt>2.4:
		percentage=50
	elif volt>2.3:
		percentage=25
	else:
		percentage=0
	return percentage

def generate_message(codes):
	message=""
	for code in codes:
		if len(message)>0:
			message+=", "
		message+=CODES[code]
	return message

logger("Starting Probe")
broker = os.getenv('VV_BROKER','ha.anachronism.co.uk')
port = int(os.getenv('VV_BROKER_PORT',1883))
topic = "python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = os.getenv('VV_BROKER_USERNAME')
password = os.getenv('VV_BROKER_PASSWORD')
api_key = os.getenv('VV_API_KEY')
my_probes = os.getenv('VV_MY_PROBES',"")
probe_frequency=int(os.getenv('VV_PROBE_FREQUENCY',600))
if probe_frequency<600:
	probe_frequency=600
client=connect_mqtt(client_id,broker,port,username,password)
client.on_disconnect = on_disconnect
while True:
	for vprobe_sn in my_probes.split(','):
		url = f"https://nix2n3nq4jwhs6txesrbn4ih5a0tvacw.lambda-url.eu-west-1.on.aws/api-v1/get-live-data?api-key={api_key}&vprobe-sn={vprobe_sn}"
		status_code=429
		while status_code==429:
			response = requests.get(url)
			status_code = response.status_code
			if status_code==429:
				logger("Got 429 - backing off for 60 seconds")
				time.sleep(60)
		if status_code!=200:
			break
		data = response.json()
		sn=f"vplant_sn{str(data['sn']).zfill(8)}"
		logger(f"Updating: {vprobe_sn}")
		create_vortex(client,data)
		time.sleep(5)
		data["batt"]=battery_calc(data["batt"])
		message=generate_message(data["message"])
		for trim in ['INDICATORS','SENSORS','message']:
			del data[trim]
		logger(f"Publising state to {vprobe_sn}")
		publish(client,f"{sn}/state", json.dumps(data).encode("utf-8"))
		logger(f"Publising state/message to {vprobe_sn}")
		publish(client,f"{sn}/state/message", message.encode("utf-8"))
	logger(f"Sleeping for {probe_frequency} seconds")
	time.sleep(probe_frequency)
