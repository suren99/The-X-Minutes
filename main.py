import requests
import json
import operator
import thread
import threading
import time
import sys
import os
import math
import Queue

X = 10
no_of_threads = 10

class bittrex:
    def __init__(self):
        self.url="https://bittrex.com/api/v1.1/public/"

    def get_currencies(self):
        try:
            response = requests.get(self.url + "getcurrencies")
            return response.content
        except Exception:
            time.sleep(1)
            return self.get_currencies()

    def get_price(self,market):
        try:
            response = requests.get(self.url + "getticker"+"?market="+market)
       # print response.content
            return response.content
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            return self.get_price(market)
            #r.status_code = "Connection refused"

class Parser:
    def extract(self,response):
        try:
            if response==None:
                return None
            response = response.replace("''","")
            response = json.loads(response)
            result = response['result']
            return result
        except:
            pass

    def ext_cur(self,result):
        cur = []
        for each in result:
            cur.append(each["Currency"])
        return cur
        
    def ext_price(self,result):
        try:
            return result["Last"]
        except:
            return -1

lock = threading.Lock()
start_price = {}
price_change = {}
Q = Queue.Queue()
cnt = 0

def work():
    global ext_int,cnt
    while True:
        currency = Q.get()
        if currency is None:
            Q.task_done()
            break
        if currency is not "Timeout":
            price = parser.ext_price(parser.extract(web.get_price("BTC-"+currency)))
        lock.acquire()
        if currency is "Timeout":
            for key in start_price:
                start_price[key] = 0
        else:
            if currency not in start_price or start_price[currency] == 0:
                start_price[currency] = price
            if price is None:
                lock.release()
                Q.task_done();
                continue;
            price_change[currency] = (price - start_price[currency])/start_price[currency]
            if not ext_int:
                for k,v in  sorted(price_change.items(), key = operator.itemgetter(1), reverse = True)[:6]:
                    sys.stdout.write("{0}:{1:.8f}% ".format(k,v))
            sys.stdout.flush()
            sys.stdout.write("\r")
        lock.release()
        if ext_int == None and currency is not "Timeout":
            Q.put(currency)
        Q.task_done()

def timeout():
    global ext_int
    while True:
        if ext_int is not None:
            break
        Q.put("Timeout")
        time.sleep(X * 60)

if __name__ == "__main__":
    web = bittrex()
    parser = Parser()
    thread = [None] * (no_of_threads + 1)
    ext_int = None
    for i in range(no_of_threads):
        thread[i] = threading.Thread(target = work)
        thread[i].start()
    thread[no_of_threads] = threading.Thread(target = timeout)
    thread[no_of_threads].start()
    for each_currency in parser.ext_cur(parser.extract(web.get_currencies())):
        Q.put(each_currency)
    ext_int = raw_input()
    Q.join()
    #calm up the workers
    for i in range(no_of_threads):
        Q.put(None)
    for i in range(no_of_threads + 1):
        thread[i].join()
