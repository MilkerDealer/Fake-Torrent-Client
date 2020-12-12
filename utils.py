# create torrent directory if doesn't exist
# random that gets N as an input and returns a mix of capital and non-capital letters, and numbers.
import json
import math
import pickle
import random
import string
from os import listdir
from os.path import isfile, join
from urllib.parse import urlparse


from werkzeug.utils import secure_filename

import Client


def returnClientFromDict(clientList, selectedClient):
    selectedClient = eval(selectedClient)
    for item in clientList:
        if item.dict() == selectedClient:
            return item

    print("No client found")


def load_torrents():
    path = 'pickledTorrentDataObjects'
    torrentList = []
    for item in [f for f in listdir(path) if isfile(join(path, f))]:
        file = open(path + '/' + item, "rb")
        data = pickle.load(file)
        file.close()
        data.start()
        torrentList.append(data)
    return torrentList


def save_torrent(torrent):
    """
    we will save a pickle file: much easier to pack and unpack because each TorrentData has infohash and a client object inside it.
    """
    path = 'pickledTorrentDataObjects'
    filename = secure_filename(torrent.Filename + torrent.Client.Clientname)
    output = open(path + '/' + '{}.pkl'.format(filename), 'wb')
    pickle.dump(torrent, output)
    output.close()


def save_client(clients):  # we call it save client but actually it saves the whole client list everytime
    path = 'settings'
    clients = [client.dict() for client in clients]
    with open(path + '/' + 'client_list.json', 'w') as f:
        json.dump(clients, f, indent=4)
    f.close()


def load_clients():
    path = 'settings'

    try:
        with open(path + '/' + 'client_list.json', 'r') as f:
            clients = json.load(f)
        f.close()
        clients = [Client.Client(item['randID'], item['Client'], item['Clientname'], item['userAgent'], item['port'])
                   for item in
                   clients]
        return clients

    except:
        return []


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def urlencode(bytes):
    result = ""
    valids = (string.ascii_letters + "_.").encode("ascii")
    for b in bytes:
        if b in valids:
            result += chr(b)
        elif b == " ":
            result += "+"
        else:
            result += "%%%02X" % b
    return result


def convert_size(size_bytes, toStr=True):
    if size_bytes == 0:
        if toStr:
            return "0 B"
        return 0, "B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    if toStr:
        return "{} {}".format(s, size_name[i])

    return s, size_name[i]


def getActiveTorrentsLength(torrentList: list):
    cntr = 0
    for item in torrentList:
        if item.Status:
            cntr += 1

    return cntr


def random_id(N: int):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=N))


def getSettings():
    path = 'settings'
    try:
        with open(path + '/' + 'settings.json', 'r') as f:
            generalSettings = json.load(f)
        f.close()

        return generalSettings

    except:
        return {'bandwidthDownload': 100,
                'bandwidthUpload': 2,
                'defaultPort': 6969}


def setSettings(generalSettings):
    path = 'settings'
    with open(path + '/' + 'settings.json', 'w') as f:
        json.dump(generalSettings, f, indent=4)
    f.close()


def rangeAndStr_ToBytes(range: list, type: str):
    return [toBytes(item, type) for item in range]


def toBytes(number: int, type: str):
    if type == 'KB':
        return number * (10 ** 3)

    if type == 'MB':
        return number * (10 ** 6)

    if type =='Mb':
        return number * (1/8) * (10 ** 6)

    return number

def totaldownloadspeed(torrentlist):
    downloadband = 0
    for torrent in torrentlist:
        try:
            downloadband+= torrent.DL_speed[0]
            print(torrent.DL_speed)

        except:
            pass
    return downloadband