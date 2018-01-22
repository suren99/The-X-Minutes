import requests
import json
import operator
import thread
import threading
import time
import sys
import os
import math

X = 6

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

class Bot:
    def __init__(self):
        self.lock = threading.Lock()
        self.plock = threading.Lock()
        self.currencies=parser.ext_cur(parser.extract(web.get_currencies()))
        self.dic = {}
        self.s_price = {}
        self.exit  = 0
        self.no_threads = 100
        for each_currencies in self.currencies:
            self.dic[each_currencies] = 0
            self.s_price[each_currencies] = 0
        slot_size = len(self.currencies)/self.no_threads
        cur_itr = 0
        while(cur_itr < len(self.currencies)):
           thread.start_new_thread(self.update,(cur_itr,min(cur_itr+slot_size-1,len(self.currencies)-1)))
           cur_itr+=slot_size
        thread.start_new_thread(self.show,())
        thread.start_new_thread(self.timeout,())
        x = raw_input()
        self.exit = 1
        print "Exit done"

    def show(self):
         while not self.exit:
             try:
                self.lock.acquire()
                sorted_list = sorted(self.dic.items(),key = operator.itemgetter(1),reverse=True) 
                r = 0
                for k,v in sorted_list[:7]:
 #                  self.table.add_row([k,v])
                   sys.stdout.write("{0}:{1:.8f}%  ".format(k,v)) 
                self.lock.release()
              #  sys.stdout.write("{0} ".format(self.no_threads))
                sys.stdout.flush()
                sys.stdout.write("\r")
             except:
                 self.exit = 1
                 raise 

    def timeout(self):
        while not self.exit:
            try:
                self.plock.acquire()
                for each_currencies in self.currencies:
                    self.s_price[each_currencies]=0
                self.plock.release()
                time.sleep(60 * X)
            except:
                self.exit = 1
                raise

    def update(self,start,end):
        try:
            i=start
            while True:
                if i>end:
                    i = start
                market = self.currencies[i]
                price = parser.ext_price(parser.extract(web.get_price("BTC-"+self.currencies[i])))
                if price == -1 or price == None:
                    return 
                self.plock.acquire()
                self.lock.acquire()
                if self.s_price[market] ==0:
                    self.s_price[market] = price        
                self.dic[market] = (price - self.s_price[market])/self.s_price[market]
                self.lock.release()
                self.plock.release()
                i+=1
        except:
            raise

if __name__ == "__main__":
    web = bittrex()
    parser = Parser()
    bot =  Bot()

