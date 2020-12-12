import utils


class settings:
    def __init__(self):
        settingsDict = utils.getSettings()
        self.bandwidthDownload = settingsDict['bandwidthDownload']  # Thats in megaBIT
        self.bandwidthUpload = settingsDict['bandwidthUpload']  # Thats in megaBIT
        self.defaultPort = settingsDict['defaultPort']
        self.usedDownloadBandwidth = 0
        self.usedUploadBandwidth = 0

    def isEnoughDownloadBandwidthLeft(self, requestedBandwidth):
        usedDownloadBandwidth = requestedBandwidth

        if utils.toBytes(self.bandwidthDownload) - (self.usedDownloadBandwidth + usedDownloadBandwidth) > 0:
            self.usedDownloadBandwidth += usedDownloadBandwidth
            return True

        else:
            return False

    def isEnoughUploadBandwidthLeft(self, requestedBandwidth):
        usedUploadBandwidth = requestedBandwidth

        if utils.toBytes(self.usedUploadBandwidth) - (self.usedUploadBandwidth + usedUploadBandwidth) > 0:
            self.usedDownloadBandwidth += usedUploadBandwidth
            return True

        else:
            return False

    def dict(self):
        return {'bandwidthDownload': self.bandwidthDownload,
                'bandwidthUpload': self.bandwidthUpload,
                'defaultPort': self.defaultPort}
