#! /bin/sh 

screen -d -m -S Basestation 
screen -S Basestation -p 0 -X exec python main.py
screen -S Basestation -X screen python steve.py 3.141.59.2 31415
