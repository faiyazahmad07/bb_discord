import requests
import multiprocessing
import subprocess
import os
import shutil
from discordwebhook import Discord
import time
#import threading

url = "" # Your Channel Link Goes Here. Eg: https://discord.com/api/v9/channels/:channel_id/messages?limit=10

def recv_message(url):

        headers = {
        'Authorization': '' # Your Authorization Token goes here.
        }
        response = requests.get(url,headers=headers)
        messages = response.json()
        for message in messages:
                try:
                        message['author']['bot']
                except KeyError:
                        return message['content']
        #       if message['author']['bot']:
        #               pass
        #       else:
        #       print(message)

def send(msg):
        Discord(url="<your discord webhook url>").post(content=msg)

def read_dbs():
        db = []
        with open('discord.dbs','r') as database:
                values = database.readlines()
                #print(values)
                for data in values:
                        data = eval(data)
                        db.append(data)
        return db

def update_dbs(domain,status):
        message = "{'domain':" + f"'{domain}'" + "," + "'status':" + f"'{status}'" + "}"
        with open('discord.dbs','a') as data:
                data.write(f"{message}\n")
        return True

def replace_dbs(domain,status):
        new_list = []
        with open('discord.dbs','r') as data:
                dic = data.readlines()
                #print(dic)
        for data in dic:
                data = eval(data)
                if data['domain'] == domain:
                        data['status'] = status
                new_list.append(data)
        with open('discord.dbs','w') as data:
                for val in new_list:
                        #message = "{'domain':" + f"'{do}'" + "," + "'status':" + f"'{status}'" + "}"
                        data.writelines(f"{val}\n")

#replace_dbs('chappania.com','completed')



def scanner(domain,isRepeated):
    if isRepeated:
        shutil.rmtree(domain.split('.')[0]) # Delete the existing scanned folder.
    os.mkdir(domain.split('.')[0]) # Create a New Folder.
    os.chdir(os.getcwd() + '/' + domain.split('.')[0])
    '''
    You Methodology goes here. Please use subprocess.call(<your cmd>,shell=True)
    Eg: subprocess.call('cat domains.txt | httprobe > https.txt',shell=True)
    '''
    subprocess.call(f'subfinder -d {domain} -o subfinder.txt',shell=True)
    subprocess.call(f'amass enum -d {domain} -o amass.txt',shell=True)
    subprocess.call(f'cat subfinder.txt amass.txt | sort -u > sorted.txt',shell=True)
    subprocess.call('rm -r subfinder.txt amass.txt',shell=True)
    subprocess.call('cat sorted.txt | httpx -title -o http.txt',shell=True)
    subprocess.call('nuclei -l sorted.txt -o nuclei.txt',shell=True)
    subprocess.call('naabu -l sorted.txt -o ports.txt',shell=True)
    os.chdir('..')
    if isRepeated:
        replace_dbs(domain,'re-scanned')
    else:
        replace_dbs(domain,'completed')
    send('[+] Reconnaissance Completed on {0}'.format(domain))
#        print(1)

def main():
    again = False
    message = recv_message(url) #;print(message)
    try:
        domain = message.split()[1]
    except:
        return None
    #print(domain)
    dbs = read_dbs()
    #print(dbs)
    for data in dbs:
            if data['domain'] == domain:
                    if data['status'] == 'scanning' or data['status'] == 're-scanned':
                                #send('[+] Aleady Scanning')
                            return None
                    elif data['status'] == 'completed':
                            try:
                                    message = message.split()[2]
                                    if message == "again":
                                        #shutil.rmtree(domain.split('.')[0])
                                        print(1)
                                        again = True
                                        break
                            except:
                                    #send('[+] Already Scanned')
                                    return None
    if again:
        #print(1)
        replace_dbs(domain,'scanning') # Replaces the existing status in the dbs
    else:
        update_dbs(domain,'scanning') # Add a new entry in the dbs
    send(f'[+] Reconnaisance Started on {domain}!')
    scanner(domain,isRepeated=again)
#main()

if __name__ == "__main__":
        while True:
                multiprocessing.Process(target=main).start() #Creates a new independent sub-process
                time.sleep(5)
