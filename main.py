import os
import shutil
from os import listdir
from os.path import isfile, join

from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename

import Client
import Settings
import Torrent
import utils
dirs = ['erroredTorrents', 'pickledTorrentDataObjects', 'newlyRecieved', 'settings', 'torrentFiles']
for dir in dirs:
    try:
        os.mkdir(dir)
    except:
        pass
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.torrent']
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

clientList = utils.load_clients()
torrentList = utils.load_torrents()
settingsVar = Settings.settings()



@app.route('/')
def index():
    torrentItems = [torrent.dict() for torrent in torrentList]
    totalActive = utils.getActiveTorrentsLength(torrentList)
    return render_template('index.html', torrentItems=torrentItems,
                           totalActive=totalActive, downloadspeed = utils.totaldownloadspeed(torrentList))


@app.route('/generalSettings', methods=['GET', 'POST'])
def general_settings():
    if (request.method == 'GET'):
        return render_template('generalSettings.html', settings=settingsVar.dict())

    settingsVar.bandwidthDownload = int(request.form['bandwidthUpload'])
    settingsVar.bandwidthUpload = int(request.form['bandwidthDownload'])
    settingsVar.defaultPort = int(request.form['defaultPort'])
    utils.setSettings(settingsVar.dict())

    return redirect(url_for('index'))


@app.route('/uploadFiles', methods=['POST'])
def upload_received():
    localPath = 'torrentFiles'
    justReceivedPath = 'newlyRecieved'
    errorPath = 'erroredTorrents'
    # every file we get - we add to torrentList
    selectedClient = utils.returnClientFromDict(clientList, request.form['torrentClient'])
    progress = float(request.form['progress'])
    isActive = eval(request.form['yes_no'])

    downloadRange = utils.rangeAndStr_ToBytes([int(request.form['downloadMin']), int(request.form['downloadMax'])],
                                              request.form['downloadType'])
    uploadRange = utils.rangeAndStr_ToBytes([int(request.form['uploadMin']), int(request.form['uploadMax'])],
                                            request.form['uploadType'])

    uploaded_files = request.files.getlist('file')
    for uploaded_file in uploaded_files:
        file_ext = os.path.splitext(uploaded_file.filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flash("{} is not a torrent file so it wasn't added!".format(uploaded_file.filename))
            uploaded_files.remove(uploaded_file)

    for item in uploaded_files:
        item.save(os.path.join(justReceivedPath, secure_filename(item.filename)))

    for item in [f for f in listdir(justReceivedPath) if isfile(join(justReceivedPath, f))]:
        try:
            #### WE NEED TO MAKE A FILE VERIFIER - IF THERE'S A FILE WITH EXACTLY SAME CONTENTS WE REMOVE IT.
            # ON THE SAME NOTE - IF THERES FILE WITH THE SAME NAME BUT DIFFERENT CONTENTS, WE NEED TO THINK OF A WAY TO KEEP IT.
            parsedTorrentFile = Torrent.parse(justReceivedPath + '/' + item)
            torrentItem = Torrent.TorrentData(parsedTorrent=parsedTorrentFile, client=selectedClient, status=False,
                                              downloadSpeed=downloadRange, uploadSpeed=uploadRange)
            torrentItem.Downloaded = (torrentItem.Size * progress) / 100
            torrentItem.Status = isActive
            torrentItem.start()
            torrentList.append(torrentItem)
            shutil.move(justReceivedPath + '/' + item, localPath + '/' + item)

        except Exception as e:
            shutil.move(justReceivedPath + '/' + item, errorPath + '/' + item)
            flash("{} made an error and I can't add it. Error message: {}".format(item, e))

    return redirect(url_for('index'))


@app.route('/uploadFiles', methods=['GET'])
def upload_files():
    if len(clientList) == 0:
        flash("You don't have any clients! please create one first")
        return redirect(url_for("create_client"))

    return render_template("uploadTorrents.html", torrentClients=clientList)


@app.route('/createClient', methods=['GET', 'POST'])
def create_client():
    if request.method == 'GET':
        randID = utils.random_id(12)
        return render_template("createClient.html", clients=Client.Clients, randID=randID,
                               port=settingsVar.defaultPort)

    torrentClientNickname = request.form['nickname']
    torrentClient = eval(request.form['client'])
    peerID = request.form['peerID']
    port = request.form['clientPort']
    cl1 = Client.Client(peerID, torrentClient['peerID'], torrentClientNickname, torrentClient['User-Agent'], port)
    clientList.append(cl1)
    utils.save_client(clientList)
    # we also need to add the new client to a json file list of clinets.
    # for that purpose - we will add a dict of the class to the file list.
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
    app.run(host='0.0.0.0', debug=True)
