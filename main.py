"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time
import json
import datetime

from pythonosc import udp_client

import requests             #Used to create API request objects
import arrow                #Used to get timestamps


#Function to retrieve waveHeight and wavePeriod from given co-ordinates
def retrieve_swell_data(latitude,longitude,key,start,end):
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': latitude,
            'lng': longitude,
            'start': start.timestamp(),
            'end': end.timestamp(),
            'source': 'noaa',
            'params': 'waveHeight,wavePeriod'
        },
        headers={
            'Authorization': key
        }
    )

    json_data = response.json()
    print(json.dumps(json_data, indent=1))

    waveHeight = json_data['hours'][0]['waveHeight']['noaa']
    wavePeriod = json_data['hours'][0]['wavePeriod']['noaa']


    print('Wave Height ', waveHeight)
    print('Wave Period ', wavePeriod)

    output = [waveHeight,wavePeriod]

    return output

#Function to send waves to supercollider
def send_waves(waveHeight,waveFrequency):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
    help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=57120,
    help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    client.send_message("/create",1)

    #for x in range(15):
    #   client.send_message("/height", waveHeight)
    #   client.send_message("/freq", waveFrequency)
    #   time.sleep(1)

    #client.send_message("/free",1)

    client.send_message("/height", waveHeight)
    client.send_message("/freq", waveFrequency)



if __name__ == "__main__":

    #Generate input for stormglass API
    key = "b3878048-ebf0-11eb-862d-0242ac130002-b38780ca-ebf0-11eb-862d-0242ac130002"
    latitude = 45.583290
    longitude = -22.442723
    start = arrow.now()
    end = arrow.now()
    start = start.shift(hours=+1)
    end = start.shift(hours=+1)

            
    now = datetime.datetime.now()
    hour = now.hour
    lastHour = hour - 1

    while(1):

        now = datetime.datetime.now()
        hour = now.hour

        if(hour > lastHour):

            lastHour = hour

            #Get output  from stormglass API
            output = retrieve_swell_data(latitude,longitude,key,start,end)

            #Read output to variables for calling send_waves
            waveHeight = output[0]
            wavePeriod = output[1]
            #Calculate wave frequency for calling send_waves
            waveFrequency = 1/wavePeriod

            #Send waves
            send_waves(waveHeight,waveFrequency)
        



  