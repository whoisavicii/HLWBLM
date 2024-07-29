#coding:utf-8

import os

#masscan端口扫描
def masscan():
    os.system('masscan -iL ip.txt -p 1-65535 -oL masscannewtmp.txt --rate=2000')

#masscan扫描结果解析
def newresult():
    masscanfile = open("masscannewtmp.txt", "r")
    masscanfile.seek(0)
    for line in masscanfile:
        if line.startswith("#"):
            continue
        if line.startswith("open"):
            line = line.split(" ")
            with open("masscanconvert.txt", "a") as f:
                f.write(line[3]+":"+line[2]+"\n")
    masscanfile.close()
    os.system('rm -rf masscannewtmp.txt')

#dismap指纹识别
def dismap():
    addfile = open("masscanconvert.txt", "r")
    addfile.seek(0)
    addlist = []
    for line in addfile:
        addlist.append(line.strip())
    addfile.close()
    for i in addlist:
        i = i.split(":")
        os.system('./dismap -i '+i[0]+' -p '+i[1]+' --np -j dismap.json')

def httpx():
    if os.path.exists("masscanconvert.txt"):
        os.system('./httpx -l masscanconvert.txt -nc  -j -o httpx.json')




def main():
    masscan()
    newresult()
    httpx()
    dismap()
    
if __name__ == '__main__':
    main()

