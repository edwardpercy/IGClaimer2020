import atexit
import datetime
import importlib
import itertools
import json
import logging
import os
import pickle
import random
import re
import signal
import sqlite3
import sys
import time
#import eventlet 

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from requests.exceptions import Timeout
required_modules = ["requests","fake_useragent"]

for modname in required_modules:
    try:
        # try to import the module normally and put it in globals
        globals()[modname] = importlib.import_module(modname)
    except ImportError as e:
        if modname != "fake_useragent":
            print(
                f"Failed to load module {modname}. Make sure you have installed correctly all dependencies."
            )
            if modname == "instaloader":
                print(
                    f"If instaloader keeps failing and you are running this script on a Raspberry, please visit this project's Wiki on GitHub (https://github.com/instabot-py/instabot.py/wiki) for more information."
                )
            quit()

class InstaChecker:   
    Letters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]  
    url = "https://www.instagram.com/"
    url_attempt = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
    cookie = ""
    user_agent = "" ""
    accept_language = "en-US,en;q=0.5"
    csrf_token = ""
    def __init__(self,proxy,console,apps):
        self.console = console
        self.app = apps
        self.list_of_ua = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.7.01001)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.5.01003)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8",
            "Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
            "Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows NT 5.1; rv:5.0.1) Gecko/20100101 Firefox/5.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.02",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1",
            "Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.0) Opera 7.02 Bork-edition [en]",
        ]
        try:
            fallback = random.sample(self.list_of_ua, 1)
            fake_ua = fake_useragent.UserAgent(fallback=fallback[0])
            self.user_agent = str(fake_ua)
        except:
            fake_ua = random.sample(self.list_of_ua, 1)
            self.user_agent = self, str(fake_ua[0])

        self.s = requests.Session()
      
       
        if proxy != "":
            #proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
            self.s.proxies.update(proxies)
        
        while(self.Retrieve_Cookie() != 0):
            
            print("Get COOKIE")
            

        
            
    def Update_Proxy(self,proxy):
        proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
        self.s.proxies.update(proxies)

    def Retrieve_Cookie(self):
        try:
            self.s.headers.update(
                {
                    "Accept": "*/*",
                    "Accept-Language": self.accept_language,
                    "Accept-Encoding": "gzip, deflate, br",
                    'cache-control': 'max-age=0',
                    "Connection": "keep-alive",
                    "Host": "www.instagram.com",
                    "Origin": "https://www.instagram.com",
                    "Referer": "https://www.instagram.com/accounts/emailsignup/",
                    "User-Agent": self.list_of_ua[random.randint(0,len(self.list_of_ua)-1)],
                    "X-Instagram-AJAX": "1",
                    'cookie': 'ig_cb=1; rur=FTW; mid=XSIcSgALAAG64cr0F1qXYubvKPXg',
                    "X-Requested-With": "XMLHttpRequest",
                }
            )

            time.sleep(5 * random.random())

            # with eventlet.Timeout(3):
            #     refresh_cookie = self.s.get(
            #         self.url, allow_redirects=True
            #     )
            
            refresh_cookie = self.s.get(
                self.url, allow_redirects=True, timeout=3
            )
            
            if (refresh_cookie.status_code != 200 and refresh_cookie.status_code != 400):  # Handling Other Status Codes and making debug easier!!
                
                self.console.append("Request Cookie Error")
                #self.console.append("Here is more info for debbugin or creating an issue")
                self.app.processEvents()
                print("=" * 15)
                print("Response Status: ", refresh_cookie.status_code)
                print("=" * 15)
                print("Response Content:\n", refresh_cookie.text)
                print("=" * 15)
                print("Response Header:\n", refresh_cookie.headers)
                print("=" * 15)
                return 2
            
            
            
            self.csrf_token = re.search('(?<="csrf_token":")\w+', refresh_cookie.text).group(0)
            
            self.s.headers.update({"X-CSRFToken": self.csrf_token})

            
            print("Cookie = " + str(self.csrf_token))
            return 0
            # except:
            #     self.console.append("PROXY ERROR - TRY AGAIN WITH NEW PROXY")
            #     self.app.processEvents()
        except:
            self.console.append("BAD PROXY")
            return 2

    def check(self, check_name, Tproxy):

        proxies = {"http": f"http://{Tproxy}", "https": f"https://{Tproxy}"}
        self.s.proxies.update(proxies)

        if self.csrf_token != "":
            self.s.headers.update(
                {
                    "Accept": "*/*",
                    "Accept-Language": self.accept_language,
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Host": "www.instagram.com",
                    "Origin": "https://www.instagram.com",
                    "Referer": "https://www.instagram.com/accounts/emailsignup/",
                    "User-Agent": self.list_of_ua[random.randint(0,len(self.list_of_ua)-1)],
                    "X-Instagram-AJAX": "1",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                }
            )
            #print(("Trying to check {}...".format(check_name)))
            
           
            

            self.edit_post = {
                "email": "technicalinsta4" + str(self.Letters[random.randint(0,len(self.Letters)-1)]) + "@gmail.com",
                'password': "dSsFDScv43*" + str(self.Letters[random.randint(0,len(self.Letters)-1)]),
                "username": check_name,
                "first_name": "John" + str(self.Letters[random.randint(0,len(self.Letters)-1)]),
            }


            try:
                
                #with eventlet.Timeout(3):
                login = self.s.post(
                    self.url_attempt, data=self.edit_post, allow_redirects=True
                )
                if (
                    login.status_code != 200 and login.status_code != 400
                ):  # Handling Other Status Codes and making debug easier!!
                    
                
                    print("Response Status: ", login.status_code)
                
                    return 3

                
                loginResponse = login.json()
        
            
                
            
                if loginResponse.get("dryrun_passed") == True: #Claimable
                    return 1
                elif loginResponse.get("dryrun_passed") == False: #Taken
                    return 0
                else:
                    return 3
                
            except:
               
                return 4


    def filter(self, check_name, Tproxy):

        proxies = {"http": f"http://{Tproxy}", "https": f"https://{Tproxy}"}
        self.s.proxies.update(proxies)

        if self.csrf_token != "":
            self.s.headers.update(
                {
                    "Accept": "*/*",
                    "Accept-Language": self.accept_language,
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Host": "www.instagram.com",
                    "Origin": "https://www.instagram.com",
                    "Referer": "https://www.google.co.uk/",
                    "User-Agent": self.list_of_ua[random.randint(0,len(self.list_of_ua)-1)],
                    "X-Instagram-AJAX": "1",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                }
            )
            print(("Trying to check {}...".format(check_name)))
            
           
            

            
            url_filter = f"https://www.instagram.com/{check_name}"

            try:
                
            #with eventlet.Timeout(3):
                login = self.s.post(
                    url_filter, allow_redirects=True
                )
               

                text = login.text
                if ("The link you followed may be broken, or the page may have been removed." in text):
                    print ("GOOD NAME")
                    return 0

                elif ("Instagram photos and videos" in text):
                    print("TAKEN")
                    return 1
                
                else:
                    return 3

            
                
            except:
            
                print("EXCEPTION ERROR")
                return 3
           

