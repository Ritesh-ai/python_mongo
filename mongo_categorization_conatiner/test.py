import os
import sys
import urllib.request
import cv2
import time
import re
import time
import pandas as pd

from pymongo import MongoClient


client = MongoClient('localhost:27017')
db = client.eb
collection = db.users

for post in collection.find():
    try:
        print(post['user_fb_url'])
    except:
        # for key,value in post.items():
        #     print(key,"------------",value)
        # break
        pass