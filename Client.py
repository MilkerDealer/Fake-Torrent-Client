import requests, bencoding, utils


class Client:
    def __init__(self, randID, clientVersion, clientname, userAgent, port):
        self.randID = randID
        self.Client = clientVersion
        self.Clientname = self.__str__() if clientname == "" else clientname
        self.userAgent = userAgent
        self.port = port

    def __str__(self):
        return self.Client + self.randID

    def dict(self):
        return {
            'randID': self.randID,
            'Client': self.Client,
            'Clientname': self.Clientname,
            'userAgent': self.userAgent,
            'port': self.port
        }

    def StartAnnounce(self, torrentObj):
        # we get a torrentData and run it on it's client.
        # this is the first announce - we announce the start of the torrent
        try:
            HTTP_HEADERS = {
                "Accept-Encoding": "gzip",
                "User-Agent": self.userAgent
            }
            tracker_url = torrentObj.announce_url
            http_params = {
                "info_hash": torrentObj.infoHash,
                "peer_id": self.__str__(),
                "port": self.port,
                "uploaded": torrentObj.Uploaded,
                "downloaded": torrentObj.Downloaded,
                "left": torrentObj.Size - torrentObj.Downloaded,
                "event": "started",
                "compact": 1,
                "numwant": 200,
                "supportcrypto": 1,
                "no_peer_id": 1
            }
            req = requests.get(tracker_url, params=http_params,
                               headers=HTTP_HEADERS)
            info = bencoding.decode(req.content)
            torrentObj.waitInterval = info[b"interval"]
            torrentObj.Seeders = int(info[b"complete"])
            torrentObj.Leechers = int(info[b"incomplete"])
            print('announce success')

        except:
            # if we couldn't announce, its not big deal: we will announce again next time that's needed.
            # it is also possible to sleep 10 seconds and than call the function again but it's not a part of the algorithm.
            pass

    def resumedAnnounce(self, torrentObj):
        # we get a torrentData and run it on it's client.
        # this is the first announce - we announce the start of the torrent
        try:
            HTTP_HEADERS = {
                "Accept-Encoding": "gzip",
                "User-Agent": self.userAgent
            }

            http_params = {
                "info_hash": torrentObj.infoHash,
                "peer_id": self.__str__(),
                "port": self.port,
                "uploaded": torrentObj.Uploaded,
                "downloaded": torrentObj.Downloaded,
                "left": torrentObj.Size - torrentObj.Downloaded,
                "compact": 1,
                "numwant": 200,
                "supportcrypto": 1,
                "no_peer_id": 1
            }
            req = requests.get(torrentObj.announce_url, params=http_params,
                               headers=HTTP_HEADERS)
            info = bencoding.decode(req.content)
            torrentObj.waitInterval = info[b"interval"]
            torrentObj.Seeders = int(info[b"complete"])
            torrentObj.Leechers = int(info[b"incomplete"])

        except:
            # if we couldn't announce, its not big deal: we will announce again next time that's needed.
            # it is also possible to sleep 10 seconds and than call the function again but it's not a part of the algorithm.
            pass


Clients = [{"Name": "qBittorrent 4.3.1",
            "peerID": "-qB4310-",
            "User-Agent": "qBittorrent/4.3.1"
            },
           {"Name": "qBittorrent 4.3.0",
            "peerID": "-qB4300-",
            "User-Agent": "qBittorrent/4.3.0"
            },
           {"Name": "qBittorrent 4.2.5",
            "peerID": "-qB4250-",
            "User-Agent": "qBittorrent/4.2.5"
            },
           {"Name": "qBittorrent 4.2.3",
            "peerID": "-qB4230-",
            "User-Agent": "qBittorrent/4.2.3"
            },
           {"Name": "qBittorrent 4.2.1",
            "peerID": "-qB4210-",
            "User-Agent": "qBittorrent/4.2.1"
            },
           {"Name": "Transmission 3.00",
            "peerID": "-TR3000-",
            "User-Agent": "Transmission/3.00"
            },
           {"Name": "uTorrent 2.2.1",
            "peerID": "-UT2210-",
            "User-Agent": "uTorrent/2210(25110)"
            }]