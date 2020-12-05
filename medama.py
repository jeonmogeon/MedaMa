import requests
import os
import sys
import json
import re
import datetime
import socket

proxyserver = 'localhost'
proxyDict = {"https" : proxyserver}
if proxyserver == 'localhost':
    proxyDict = {}
    
path_dir = 'downloads'
if not os.path.exists(path_dir):
    os.mkdir(path_dir)
if not os.path.exists(os.path.join("data","db")):
    os.mkdir(os.path.join("data","db"))

db = {
    "id":os.path.join(os.path.join("data","db"),"id"),
    "tag":os.path.join(os.path.join("data","db"),"tag"),
    "language":os.path.join(os.path.join("data","db"),"language"),
    "type":os.path.join(os.path.join("data","db"),"type")
    }
 
for path in db.values():
    if not os.path.exists(path):
        os.mkdir(path)

def download_from_id(id):
    jsurl = f'https://ltn.hitomi.la/galleries/{id}.js'
    jsreq = requests.get(jsurl, proxies=proxyDict)
    if(jsreq.status_code!=200):
        print(f"[{id}] Error (ID Not exists)")
        return 0

    path = os.path.join(path_dir, str(id))
    if not os.path.exists(path):
        os.mkdir(path)

    galjson = json.loads(jsreq.content.decode('utf-8').split(' = ')[1].replace('null','"null"'))

    if str(id) != galjson['id']:
        print(f"[{id}] Error (Fetch Error)")
        return 0

    tagfile = open(os.path.join(path, 'info.tag'), 'w')
    tagfile.write("__GalleryID__\n")
    tagfile.write(f"{id}\n")
    tagfile.write("__ReaderURL__\n")
    tagfile.write(f"{f'https://hitomi.la/reader/{id}.html'}\n")
    tagfile.write("__TagInfo__\n")
    for tags in galjson['tags']:
        if 'female' in tags.keys():
            if tags['female']:
                sex = "female:"
            elif tags['male']:
                sex = "male:"
        else:
            sex = ""
        tagfile.write(f"{sex}{tags['tag'].replace(' ','_')}\n")
    tagfile.write("\n__DownloadInfo__\n")
    tagfile.write(f"Time: {str(datetime.datetime.now())}\n")
    tagfile.write(f"Proxy: {proxyserver}\n")
    tagfile.write(f"ClientIP: {socket.gethostbyname(socket.getfqdn())}\n")
    tagfile.write(f"User: {str(socket.gethostname())}\n")
    tagfile.write(f"Downloader: MedaMa\n")
    tagfile.close()

    for files in galjson['files']:
        print(f"\r[{id}] {files['name'].split('.')[0]}/{len(galjson['files'])-1}", end='')
        name = files['name']
        fileurl = url_from_file_json(files)
        header = {'Referer':f'https://hitomi.la/reader/{id}.html'}
        filereq = requests.get(fileurl, headers=header, proxies=proxyDict)
        
        if filereq.status_code != 200:
            print(f"\n[{id}] Error (Download Error)")
        else:
            imgfile = open(os.path.join(path, name),'wb')
            imgfile.write(filereq.content)
            imgfile.close()
    print(f"\r[{id}] Download Complete")

def data_from_id(id):
    data = {}
    file_list = []
    jsurl = f'https://ltn.hitomi.la/galleries/{id}.js'
    jsreq = requests.get(jsurl, proxies=proxyDict)

    if(jsreq.status_code!=200):
        print(f"[{id}] Error (ID Not exists)")
        return 0
    
    galjson = json.loads(jsreq.content.decode('utf-8').split(' = ')[1].replace('null','"null"'))

    if str(id) != galjson['id']:
        print(f"[{id}] Error (Fetch Error)")
        return 0

    for files in galjson['files']:
        fname = files['name']
        hash = files['hash']
        fileurl = url_from_file_json(files)
        file_dict = {'file':fname,'hash':hash,'url':fileurl}
        file_list.append(file_dict)

    data['id'] = id
    data['language'] = galjson['language']
    tag_list = []
    for tags in galjson['tags']:
        if 'female' in tags.keys():
            if tags['female']:
                sex = "female:"
            elif tags['male']:
                sex = "male:"
        else:
            sex = "both:"
        tag_list.append(f"{sex}{tags['tag'].replace(' ','_')}")
    data['tag'] = tag_list
    data['type'] = galjson['type']
    data['date'] = galjson['date']
    data['files'] = file_list
    print(f"\r[{id}] URL Fetch Complete")
    return data

def url_from_file_json(files):
        hash = files['hash']
        if files['haswebp']:
            ext = 'webp'
            extu = 'webp'
            subd2='a'
        elif files['hasavif']:
            ext = 'avif'
            extu = 'avif'
            subd2='a'
        else:
            ext = files['name'].split('.')[1]   
            extu = 'images'
            subd2='b'
        hashafter = f"{hash[len(hash)-1]}/{hash[len(hash)-3]}{hash[len(hash)-2]}/{hash}"
        paInt = f'{hash[len(hash)-3]}{hash[len(hash)-2]}'
        if(int(paInt,16)>int(0x09) and int(paInt,16)<int(0x30)):
            nof = 2
            g = int(paInt,16)
        elif(int(paInt,16)<int(0x09)):
            nof=2
            g=1
        else:
            nof=3
            g = int(paInt,16)
        subd = chr(97+g%nof)
        fileurl = f"https://{subd}{subd2}.hitomi.la/{extu}/{hashafter}.{ext}"
        return(fileurl)

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="-db":
            print("DB Mode")
            for id in range(0,2000000):
                data_dict = data_from_id(id)
                if data_dict:
                    open(os.path.join(db['id'],f"{id}.tld"),'a').write(json.dumps(data_dict))
                    for tag in data_dict['tag']:
                        sex = os.path.join(db['tag'],f"{tag.split(':')[0]}")
                        if not os.path.exists(sex):
                            os.mkdir(sex)
                        open(os.path.join(sex,f"{tag.split(':')[1]}.tld"),'a').write(str(id)+"\n")
                    open(os.path.join(db['language'],f"{data_dict['language']}.tld"),'a').write(str(id)+"\n")
                    open(os.path.join(db['type'],f"{data_dict['type']}.tld"),'a').write(str(id)+"\n")
            sys.exit()

    id = input("? ")
    download_from_id(id)

# 해시가 12313123123123asda 이러면 끝의 세자리 sda에서 a / sd / $hash
# https:// a . hitomi . la / images / (해시변환) . 확장자
# 근데 앞에 a.hitomi.la를 바꿈 subdomain_from_url으로
# 앞에 링크 (어떤거 대신 한자리 숫자)/(어떤거2 대신 두자리 숫자)/(어떤거3 아무거나) 이니까 앞에 해시처리한거겠지
# (어떤거2 대신 두자리 숫자) 그거를 16진수 처리 하고 아니면 b
# g라 하자 그거랑 0x09 0x30 이면 nof =2 g는그대로 크면 0x09 보다 작으면 g=1 nof=2 아무것도 아니면 nof=3 g그대로
# chr( 97 + g % nof) + b (a일수도) . hitomi.la