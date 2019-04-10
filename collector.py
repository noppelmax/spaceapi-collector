#!/bin/python

import os
import logging
import json
import configparser
import requests

from influxdb import InfluxDBClient
from multiprocessing import Process, Manager

DBNAME = "SPACEAPI_STATS"
USE_INFLUX = True


if USE_INFLUX:
    client = InfluxDBClient("localhost",8086,"root","root",DBNAME)
    client.create_database(DBNAME)
    client.switch_database(DBNAME)

VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 0
VERSION = "v" + str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + "." + str(VERSION_PATCH)

logger = logging.getLogger("collector.py")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.info("Running version " + VERSION)


def loadSpaceAPI(spacename,points):

    try:
        url = data[spacename]
    except Exception as e:
        logger.error(spacename + ": " + str(e))
        return
    
    try:
        r = json.loads(requests.get(url=url,timeout=1).text)
    except Exception as e:
        logger.error(spacename + ": " + str(e))
        return
    
    try:
        if r["api"] == "0.13":
            if r["state"] and r["state"]["open"]:
                p = {
                    "measurement": spacename,
                    "fields": {
                        "doorstate": r["state"]["open"]
                    }
                }
                
                print(p)
                points.append(p)
    except Exception as e:
        logger.error(spacename + ": " + str(e))


if __name__ == '__main__':
    manager = Manager()
    points = manager.list()
    processes = []
    with open('directory.json',encoding='utf-8') as f:
        data = json.load(f)
        for spacename in data:
            p = Process(target=loadSpaceAPI, args=(spacename,points))
            processes.append(p)
            p.start()

    for p in processes:
        p.join()

    logger.info("JOINED")

    
    if USE_INFLUX:
        logger.info("Write to INFLUX" + str(points))
        client.write_points(points)
