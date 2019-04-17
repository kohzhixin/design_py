#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import firebase_admin
from firebase_admin import firestore, credentials
from numpy.random import choice, randint

import time

cred = credentials.Certificate("C:/Users/kohzh/Downloads/design-8d4ff-firebase-adminsdk-b7b9t-0a11c527ed.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
deps = db.collection("departures_2h")

def add_to_db_2h():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver_dep = webdriver.Chrome(r"C:\Users\kohzh\Downloads\chromedriver_win32\chromedriver.exe", options=options)
    driver_dep.get("http://www.changiairport.com/en/flight/departures.html")
    link = driver_dep.find_element_by_class_name("js--load-later")
    link.send_keys(Keys.RETURN)
    info_dep = driver_dep.find_elements_by_xpath("//*[@id=\"page\"]/div/main/div/div/div[2]/div[3]/div[2]")[0].text
    driver_dep.close()
    print("pulled departure info")

    info_list_dep = info_dep.split("\n")[4:]

    for i in info_list_dep:
        if "Codeshare" in i or i == "Check-in Row/Door" or i == "Boarding Gate":
            info_list_dep.remove(i)

    #print(info_list_dep)
    nested_list_dep = []

    while len(info_list_dep) > 2:
        if ":" in info_list_dep[0]:
            info_list_dep.insert(0, "")
        if ":" not in info_list_dep[2]:
            info_list_dep.insert(2, "")
        if info_list_dep[0] == "CANCELLED":
            info_list_dep.insert(8, "")
        nested_list_dep.append(info_list_dep[:9])
        info_list_dep = info_list_dep[9:]

    for i in nested_list_dep:
        i = {"Status": i[0],
           "Time": i[1],
           "Revised Time": i[2],
           "To": i[3],
           "Flight No": i[4],
           "Flight": i[5],
           "Terminal": i[6],
           "Check-in Row/Door": i[7],
           "Boarding Gate": i[8]}
        deps.add(i)
    print("pushed departure info")

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).get()
    deleted = 0
    for doc in docs:
#        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


try:
    while True:
        #try: 
        if len([i for i in deps.get()]) != 0:
            delete_collection(deps, len([i for i in deps.get()]))
        add_to_db_2h()
        print("time:", time.ctime())
        time.sleep(60 * 5) # update database every 5 minutes
        #except Exception:
         #   print("catch exception")
except KeyboardInterrupt:
    print("end")
