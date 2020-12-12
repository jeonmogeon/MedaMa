import base64
import os 

dir = input('? ')

def enc():
    files = []
    filelist = os.listdir(dir)
    tagfile = ''
    for filen in filelist:
        ext = filen.split('.')[len(filen.split('.'))-1]
        if ext=="jpg" or ext=="png" or ext=="webp":
            files.append(filen)
        if ext=="tag":
            tagfile = filen

    imaged = open(f'{dir}.data','w')
    if tagfile:
        tagdata = open(os.path.join(dir,tagfile),'r').read()
        imaged.write(tagdata+"\n__ImageData__\nEncoding: base64\nData:\n$$START%%")
    for filepath in files:
        image = open(os.path.join(dir,filepath),'rb').read()
        imaged.write(base64.b64encode(image).decode()+"$$NEWLINE%%")
    imaged.close()

def dec():
    b64str = open(f'{dir}.data','r').read().split('$$START%%')[1]
    num = 1
    for b64 in b64str.split('$$NEWLINE%%'):
        if b64:
            image = open(f'res/{num}.jpg','wb').write(base64.b64decode(b64))
            num+=1

enc()