#!/usr/bin/python
"""
This programme gathers an hourly wave forecasts from the Stormglass 
API and sends wave frequency and height data to Supercollider via OSC
"""
import argparse
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
            'start': start,
            'end': end,
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

    print('Wave Height from API ', waveHeight)
    print('Wave Period from API ', wavePeriod)

    output = [waveHeight,wavePeriod]

    return output


#Function to send wave data to supercollider via OSC
def send_waves(waveHeight,waveFrequency):
    client.send_message("/height", waveHeight)
    client.send_message("/freq", waveFrequency)


if __name__ == "__main__":

    print("Python script initiated")
    time.sleep(60)

    #Initiate Synth
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
    help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=57120,
    help="The port the OSC server is listening on")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)

    client.send_message("/create",1)

    #Generate input for stormglass API
    key = "b3878048-ebf0-11eb-862d-0242ac130002-b38780ca-ebf0-11eb-862d-0242ac130002"
    latitude = 35.481402
    longitude = 12.511284
    start = arrow.now()
    end = arrow.now()
    start = start.shift(hours=+1)
    end = start.shift(hours=+1)

    print("Start ",start)
    print("End: ",end)
    #start = start.timestamp()
    #end = end.timestamp()

    while(1):

      #Get output  from stormglass API
      output = retrieve_swell_data(latitude,longitude,key,start,end)

      #Read output to variables for calling send_waves
      waveHeight = output[0]
      wavePeriod = output[1]
      #Calculate wave frequency for calling send_waves
      waveFrequency = 1/wavePeriod

      print('Wave Height Sent', waveHeight)
      print('Wave Period Sent', wavePeriod)
      print('Wave Frequency Sent', waveFrequency)

      #Send waves
      send_waves(waveHeight,waveFrequency)

      time.sleep(3600)
