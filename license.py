import requests
import json
from bs4 import BeautifulSoup
import uuid 


def encode_mac():
    mac = hex(uuid.getnode())
    mac = int(str(mac), 16)
    mac = ((mac /234) - 643) / 4 +5 * 3
    return str(mac)

def licence_check():
   
    try: 
        url = "https://pastebin.com/mhz8bhVV"
        s = requests.Session()
        response = s.get(url, allow_redirects=True)

        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, 'html.parser')
            soup = soup.find_all('title')[0].get_text()
            soup = soup[:2]
            
            #ALLOW PROGRAM TO RUN
            if (soup[0] == '0' and soup[1] == '0'): #DO NOT RUN
                return 0

            elif (soup[0] == '0' and soup[1] == '1'): #DO NOT RUN
                return 0

            elif (soup[0] == '1' and soup[1] == '0'): #LICENCE FILE NEEDED
                try:
                    f = open("check.id")
                    contents = f.read()
                    f.close()
                    if (contents == encode_mac()):
                        return 1
                    else:
                        return 0
                except FileNotFoundError:
                    return 0
                finally:
                    f.close()

            elif (soup[0] == '1' and soup[1] == '1'): #LICENCE FILE CAN BE CREATED
                try:
                    f = open("check.id")
                    contents = f.read()
                    f.close()
                    if (contents == encode_mac()):
                        return 1
                    else:
                        f = open('check.id','w')
                        f.write(encode_mac())
                        f.close()
                        return 1
                except FileNotFoundError:
                    f = open('check.id','w')
                    f.write(encode_mac())
                    f.close()
                    return 1
                finally:
                    f.close()

        
        else:
            return 0

    except:
        return 0
 


