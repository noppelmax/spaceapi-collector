#!/bin/python

import os
import logging
import json
import configparser
import requests

from influxdb import InfluxDBClient

DBNAME = "SPACEAPI_STATS"

#client = InfluxDBClient("localhost",8086,"root","root",DBNAME)
#client.create_database(DBNAME)
#client.switch_database(DBNAME)

VERSION_MAJOR = 0
VERSION_MINOR = 1
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


with open('directory.json',encoding='utf-8') as f:
    data = json.load(f)
    for spacename in data:
        try:
            url = data[spacename]
        except Exception as e:
            logger.error(spacename + ": " + str(e))
            continue

        try:
            r = json.loads(requests.get(url=url).text)
        except Exception as e:
            logger.error(spacename + ": " + str(e))
            continue

        try:
            if r["api"] == "0.13":
                if r["state"]:
                    p = {
                        "measurement": spacename,
                        "fields": {
                            "doorstate": r["state"]["open"]
                        }
                    }
                    print(p)
        except Exception as e:
            logger.error(spacename + ": " + str(e))
