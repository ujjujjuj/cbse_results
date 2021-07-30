import requests
from bs4 import BeautifulSoup
import re
import os

from config import *

dat = {}


def toPascalCase(s):
    return ' '.join([i[0] + i[1:].lower() for i in s.split(" ") if i])

def makeRequest(rollno,schoolcode):
    return requests.post(
        POST_URL,
        data = {
            "regno": rollno,
            "sch": schoolcode
        },
        headers = {
            "Referer":"https://testservices.nic.in/class12/Class12th21.htm"
        }
    ).content.decode("cp1252")

def getMarks(rollno,schoolcode):
    res = makeRequest(rollno, schoolcode)
    soup = BeautifulSoup(res, "html.parser")
    name = toPascalCase(soup.find("font",text="Candidate Name:").findNext("b").contents[0])
    subjectstd = soup.findAll("tr",{"bgcolor":["#ffffff","#e6e6fa"]})
    subjects = []
    totalmarks, nsubs = 0,0
    for sub in subjectstd:
        cols = sub.findAll("td",recursive=False)
        if len(cols) < 3:
            continue
        try:
            sub = toPascalCase(cols[1].find('font').text)
        except:
            with open("out.html","w",encoding="cp1252") as f:
                f.write(res)
                exit()
        try:
            marks = int(cols[4].find('font').text)
            totalmarks += marks
            nsubs += 1
            subjects.append(f"{sub}: {marks}")
        except:
            pass
    if nsubs == 0:
        perc = 0
    else:
        perc = round(totalmarks/nsubs,2)
    return [rollno,name,subjects,perc]

if __name__ == "__main__":
    results = []
    errs = 0
    rollno = ROLL_NUMBER_RANGE[0]
    while rollno <= ROLL_NUMBER_RANGE[1]:
        if errs > 60:
            print("Too many errors. Exiting...")
            break
        try:
            result = getMarks(rollno,SCHOOL_CODE)
            print(f"Downloaded result for {rollno}: {result[1]}")
            rollno += 1
            errs = 0
            results.append(result)
        except AttributeError:
            errs += 1
            rollno += 1
        except Exception as e:
            print(e)
            errs += 1
    with open("results.html","w") as fout:
        with open("template.html","r") as fin:
            fout.write(fin.read().replace("ARRAY_HERE",str(results)))
    print("Saved results.html")
