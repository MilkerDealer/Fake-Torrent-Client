import Client
import utils
from seedmageEngine import File
import time, threading
import random


def parse(filepath):
    torrentFileTemp = File(filepath)
    toReturn = {'Announce_URL': torrentFileTemp.announce,
                'fileHash': torrentFileTemp.file_hash,
                'torrentSize': torrentFileTemp.total_size,
                'torrentName': torrentFileTemp.torrent_header[b"info"][b"name"].decode("utf-8")
                }
    del torrentFileTemp
    return toReturn


class TorrentData():
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def __init__(self, parsedTorrent: dict, client: Client.Client, status: bool, downloaded: int = 0, uploaded: int = 0,
                 downloadSpeed: list = [100 * 1024, 100],  # max of 100KBPS, min of 1KBPS
                 uploadSpeed: list = [0, 0],  # range of 0 so we don't upload shit
                 alreadyStarted: bool = False):
        # FUNCTION DL_SPEED AND UP_SPEED WILL BE DECIDED VIA THE UPLOAD-DOWNLOAD ALGORITHEM
        self.Filename = parsedTorrent['torrentName']
        self.Client = client
        self.Status = status
        self.Size = parsedTorrent['torrentSize']
        self.Downloaded = downloaded
        self.Uploaded = uploaded
        self.DL_speedRange = downloadSpeed
        self.UL_speedRange = uploadSpeed
        self.Seeders = 1 # we need to figure out what to do when theres one seeder \ less.
        self.Leechers = 0
        self.DL_speed = None
        self.UL_speed = None
        self.infoHash = parsedTorrent['fileHash']
        self.announce_url = parsedTorrent['Announce_URL']
        self.alreadyStarted = alreadyStarted
        self.waitInterval = 1800  # default value that will be changed after "startAnnounce".

    def progress(self, toStr: bool = True) -> float or str:
        progressFloat = round((self.Downloaded / self.Size) * 100, 2)
        return "{} %".format(progressFloat) if toStr else progressFloat


    def start(self):
        t = threading.Thread(target=self._start)
        t.start()


    def downloadbandwidth(self):
        if self.Size == self.Downloaded:
            return 0
        if self.Seeders == 0:
            return 0
        if self.Seeders < 4:
            sizeinkb = 0
            for _ in range(self.Seeders):
                sizeinkb += random.randint(0, 20)

            sizeinb = utils.toBytes(sizeinkb, 'KB')
            if sizeinb + self.Downloaded > self.Size:
                return self.Size - self.Downloaded

            return sizeinb
        sizeinb = 0
        downloadmin = self.DL_speedRange[0]
        downloadmax = self.DL_speedRange[1]
        downloadmin = downloadmin / self.Seeders
        downloadmax = downloadmax / self.Seeders
        for _ in range(self.Seeders):
            sizeinb += random.randint(int(downloadmin), int(downloadmax))

        if sizeinb + self.Downloaded > self.Size:
            return self.Size - self.Downloaded
        return sizeinb



    def _start(self):  # starts downloading / seeding accordingly
        # this one starts on a seperate thread and works accordingly to the status
        cntrsleepsec = 0
        while True:
            if self.Status and self.Seeders > 0 :
                if self.alreadyStarted is True or (self.progress(toStr=False) > 0):  # even if its the first time, and progress is bigger than zero - than we cant announce "start"
                    # than we don't declare start
                    # need to check if all is downloaded
                    # basically we start a self-sustained function
                    totalToDownload = 0  # this will be set in the algoritem
                    totalToUpload = 0  # this will be set in the algoritem
                    bandwidth = self.downloadbandwidth()
                    print(bandwidth)
                    self.Downloaded += bandwidth
                    self.Uploaded += totalToUpload
                    self.alreadyStarted = True
                    self.DL_speed = utils.convert_size(bandwidth, toStr=False)
                    time.sleep(1)
                    cntrsleepsec += 1
                    if cntrsleepsec % self.waitInterval == 0:
                        print(cntrsleepsec, self.waitInterval)
                        print('announce!')
                        self.Client.resumedAnnounce(self)
                        cntrsleepsec = 0

                else:
                    # than we need to announce start, and than change the state of "alreadyStarted" To true
                    self.alreadyStarted = True
                    # we just announce to get detail, than we need to keep download and announce again only next time
                    self.Client.StartAnnounce(self)
                    time.sleep(1)

            # every loop of this while-loop should take a second. every second we update the cntr and woohoo
            utils.save_torrent(self)

    def dict(self, default: bool = True) -> dict:
        if default:
            return {"Filename": self.Filename,
                "Client": self.Client.Clientname,
                "Status": "Active" if self.Status else "Pasued",
                "Size": utils.convert_size(self.Size),
                "Downloaded": utils.convert_size(self.Downloaded),
                "Uploaded": utils.convert_size(self.Uploaded),
                "DL_speed": self.DL_speed,
                "UL_speed": self.UL_speed,
                "Seeders": self.Seeders,
                "Leechers": self.Leechers,
                "Progress": self.progress()
                }

        return {
            "Filename": self.Filename,
            "Client": self.Client.Clientname,
            "Status": "Active" if self.Status else "Pasued",
            "Size": utils.convert_size(self.Size),
            "Downloaded": utils.convert_size(self.Downloaded),
            "Uploaded": utils.convert_size(self.Uploaded),
            "Seeders": self.Seeders,
            "Leechers": self.Leechers,
            "Progress": self.progress(),
            "InfoHash": self.announce_url
        }
