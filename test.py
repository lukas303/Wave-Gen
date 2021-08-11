import argparse
import random
import time

from pythonosc import udp_client

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",
help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=57120,
help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

client.send_message("/create",1)

for x in range(30):
    height = random.random()
    client.send_message("/height", height)
    freq = random.random()*0.05
    client.send_message("/freq", freq)
    print("Freq ", freq)
    print("Height ", height)

    time.sleep(1)

client.send_message("/free",1)
