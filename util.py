import socket
import struct
from config import *
import urllib.parse
import os
import re
import datetime
import json
import traceback
import requests


def fetch_raw(addr, port, querystr):

    if querystr[0] != "?":
        querystr = "?"+querystr
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    query = b"\x00\x83" + struct.pack('>H', len(querystr) + 6) + b"\x00\x00\x00\x00\x00" + querystr.encode() + b"\x00"
    sock.settimeout(10)
    sock.connect((addr, port))

    sock.sendall(query)

    data = sock.recv(4096)

    return data


def fetch(addr, port, querystr):

    if querystr[0] != "?":
        querystr = "?"+querystr
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    query = b"\x00\x83" + struct.pack('>H', len(querystr) + 6) + b"\x00\x00\x00\x00\x00" + querystr.encode() + b"\x00"
    sock.settimeout(10)
    sock.connect((addr, port))

    sock.sendall(query)

    data = sock.recv(4096)

    parsed_data = urllib.parse.parse_qs(data[5:-1].decode())
    return {i:parsed_data[i][0] for i in parsed_data.keys()}


def fetch_bee():
    return fetch(BEE_HOST, BEE_PORT, "status")


def get_round_directories():
    rounds = []
    for year in os.listdir("./rounds"):
        try:
            for month in os.listdir("./rounds/"+year):
                for day in os.listdir("./rounds/"+year+"/"+month):
                    for round in os.listdir("./rounds/"+year+"/"+month+"/"+day):
                        try:
                            if os.path.isfile("./rounds/"+year+"/"+month+"/"+day+"/"+round+"/"+"round_end_data.json"):
                                rounds.append(["./rounds/"+year+"/"+month+"/"+day+"/"+round, int(round.split("-")[1])])
                        except:
                            print("./rounds/"+year+"/"+month+"/"+day+"/"+round)
        except:
            pass
    rounds.sort(key=lambda x: x[1])
    return rounds[:-1]

def dtl(i):
    try:
        o = list(i.values())
    except:
        o = i
    return o

def rmd(t):
    s = []
    for i in t:
        if i not in s:
           s.append(i)
    return s


def parse_round(roundid):
    round = [r for r in get_round_directories() if r[1] == roundid][0]
    parse = {}
    try:
        endround = json.load(open(round[0]+"/"+"round_end_data.json"))
        parse["escaped"] = rmd(dtl(endround["escapees"]["humans"])+dtl(endround["escapees"]["silicons"]))
        parse["abandoned"] = rmd(dtl(endround["abandoned"]["humans"])+dtl(endround["abandoned"]["silicons"]))
        parse["players"] = rmd(parse["escaped"]+parse["abandoned"])
        parse["deaths"] = rmd([player for player in parse["players"] if player["health"] <= 0])
        parse["death_count"] = len(parse["deaths"])
        parse["escaped_count"] = len(parse["escaped"])
        parse["abandoned_count"] = len(parse["abandoned"])
        parse["player_count"] = len(parse["players"])
        parse["integrity"] = endround["additional data"]["station integrity"]
        parse["id"] = round[1]
        parse["crashed"] = False

        parse["player_names"] = [str(player["name"])+" ("+str(player["ckey"])+")" for player in parse["players"]]
        parse["death_names"] = [str(player["name"])+" ("+str(player["ckey"])+")" for player in parse["deaths"]]
        parse["escaped_names"] = [(player["name"])+" ("+str(player["ckey"])+")" for player in parse["escaped"]]
        parse["abandoned_names"] = [str(player["name"])+" ("+str(player["ckey"])+")" for player in parse["abandoned"]]
    except Exception as E:
        parse["id"] = round[1]
        parse["crashed"] = True
    return parse

def parse_rounds(start,end):
    parsed = []
    rounds = get_round_directories()[::-1]

    rgerounds = rounds[start:end]
    for round in rgerounds:
        parse = {}
        try:
            endround = json.load(open(round[0]+"/"+"round_end_data.json"))
            parse["escaped"] = rmd(dtl(endround["escapees"]["humans"])+dtl(endround["escapees"]["silicons"]))
            parse["abandoned"] = rmd(dtl(endround["abandoned"]["humans"])+dtl(endround["abandoned"]["silicons"]))
            parse["players"] = rmd(parse["escaped"]+parse["abandoned"])
            parse["deaths"] = rmd([player for player in parse["players"] if player["health"] <= 0])
            parse["death_count"] = len(parse["deaths"])
            parse["escaped_count"] = len(parse["escaped"])
            parse["abandoned_count"] = len(parse["abandoned"])
            parse["player_count"] = len(parse["players"])
            parse["integrity"] = endround["additional data"]["station integrity"]
            parse["id"] = round[1]
            parse["crashed"] = False
            parsed.append(parse)
        except Exception as E:
            pass
    length = len(rounds)

    return [parsed, length]

def parse_bans(start, end):
    parsed = []
    bans = open("data/ban_unban_log.txt").read().replace("\n", " ").split(";;")[:-1]
    for ban in bans[start:end]:
        try:
            keys = ban.split("|")
            type = [key for key in keys if "TYPE" in key][0].split(": ")[1].split("/")[0].lower()

            if type == "ban":
                type = "Playing Ban"
            if type == "permaban":
                type = "Permanent Playing Ban"
            if type == "jobban":
                type = "Job Ban"
            if type == "perma-jobban":
                type = "Permanent Job Ban"
            if type == "appearance":
                type = "Appearance Ban"

            user = [key for key in keys if "BANNEE" in key][0].split(": ")[1].split("/")[0]
            banner = [key for key in keys if "BANNER" in key][0].split(": ")[1].split("/")[0]
            reason = [key for key in keys if "REASON" in key][0][8:]
            date = datetime.datetime.strptime([key for key in keys if "DATE" in key][0][6:], "%d-%b-%Y %H:%M").strftime("%d-%m-%y %H:%M")
            try:
                time = str(datetime.timedelta(minutes=int([key for key in keys if "TIME" in key][0].split(": ")[1])))
            except IndexError:
                time = "Permanent"
            try:
                job = [key for key in keys if "JOB" in key][0].split(": ")[1]
            except IndexError:
                job = None
            parsed.append({"type":type,"user": user, "banner": banner, "reason": reason, "time":time, "job":job, "date": date})
        except Exception as E:
            pass
    return [parsed, len(bans)]

def make_unique(original_list):
    unique_list = []
    for i in original_list:
        if i not in unique_list:
            unique_list.append(i)
    return unique_list

def send_message(channel,content):
    r = requests.post(DISCURL+"/channels/"+str(channel)+"/messages", data={"content": content}, headers=DISCHEADERS)
    return r.json()

def get_patreon_income():
    return requests.get("https://www.patreon.com/api/campaigns/1671674").json()["data"]["attributes"]["pledge_sum"]
