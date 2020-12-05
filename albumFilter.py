#!/usr/bin/env python3
import os
import sys
import csv
import re
import flask
from flask import Flask
from flask import render_template
import requests
import json
from flask import request
from shutil import copy
import threading
import time
import colorama

labels = list()
artists = list()
directories = list()
createdDirectories = set()
rootDirectory = str()
labelsProcessed = dict()
artistProcessed = dict()
notToDeleteItems = set()
toKeepAlbums = list()
images = dict()
runServerOrNot = True


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\33[91m'
    RED1 = "\033[0;31m"
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    YELLOW = '\033[34m'


def importLabels():
    if os.path.exists("labels.txt"):
        with open("labels.txt", "r") as labelsImport:
            for label in labelsImport:
                if "#**" not in label:
                    splitted = label.split(",")
                    labels.append(
                        [splitted[0].strip(), splitted[1].replace("\n", "").strip()])
    else:
        with open("labels.txt", "w") as create:
            create.write("#**Write here the labels, one in each line\n" +
                         "#**Format: Label Name,Label Catalog Naming\n" +
                         "#**Example: Armada Deep,ARDP")


def importArtists():
    if os.path.exists("artists.txt"):
        with open("artists.txt", "r") as artistImport:
            for artist in artistImport:
                if "#**" not in artist:
                    artist = artist.strip()
                    if " " not in artist:
                        artistFirstLetterUpper = artist[0].upper() + artist[1:]
                    else:
                        parsed = artist.split(" ")
                        for artt in parsed:
                            parsed[parsed.index(
                                artt)] = artt[0].upper() + artt[1:]
                        artistFirstLetterUpper = " ".join(parsed)
                    artists.append(artistFirstLetterUpper.replace("\n", ""))
    else:
        with open("artists.txt", "w") as create:
            create.write("#**Write here the artists, one in each line")


def listDirectoriesInside():
    with open("sortFolders.txt", "r") as file:
        global rootDirectory
        rootDirectory = file.readline()
        for fil in file:
            pathAndFile = os.path.join(rootDirectory, fil).replace("\n", "")
            createdDirectories.add(pathAndFile)
    file.close()


def listDirectories(arg):
    arr = ""
    if arg != "":
        arr = os.listdir(arg)
    return arr


def sortByLabel(file):
    if os.path.exists("labels.txt") and labels != []:
        for direc in directories:
            for label in labels:
                # if label[1] in direc:
                if re.search(r"\b"+label[1]+r"[\d]*[a-zA-Z\d]*\b", direc) != None:
                    if label[1] in labelsProcessed.keys():
                        labelsProcessed[label[1]][1].append(direc)
                        notToDeleteItems.add(direc)
                    else:
                        labelsProcessed[label[1]] = [label[0], [direc]]
                        notToDeleteItems.add(direc)
    else:
        print("Fill label text file with your labels to sort")
    formatter("label", file)


def sortByArtist(file):
    if os.path.exists("artists.txt") and artists != []:
        for direc in directories:
            for artist in artists:
                if artist in direc:
                    if artist in artistProcessed.keys():
                        artistProcessed[artist].append(direc)
                        notToDeleteItems.add(direc)
                    else:
                        artistProcessed[artist] = []
                        artistProcessed[artist].append(direc)
                        notToDeleteItems.add(direc)
    else:
        print("Fill artist text file with your artists to sort")
    formatter("artist", file)


def formatter(opType, file):
    global runServerOrNot
    global images
    getMeta(file)
    if opType == "label":
        for songList in labelsProcessed.values():
            print(f"{bcolors.OKBLUE}{bcolors.BOLD}{bcolors.UNDERLINE}---------------------------------"
                  + "Label: " + songList[0] + f"---------------------------------{bcolors.ENDC}")
            for song in songList[1]:
                if re.search(r"\b"+list(labelsProcessed.keys())[list(labelsProcessed.values()).index(songList)]+r"[\d]*[a-zA-Z\d]*\b", song) != None:
                    match = re.search(
                        r"(.*)(\b" + list(labelsProcessed.keys())[list(labelsProcessed.values()).index(songList)] + r"[\d]*[a-zA-Z\d]*\b)(.*)", song)
                    print(f"{bcolors.OKGREEN}" + match[1] + f"{bcolors.ENDC}" + f"{bcolors.UNDERLINE}{bcolors.RED}" +
                          match[2] + f"{bcolors.ENDC}" + f"{bcolors.OKGREEN}" + match[3] + f"{bcolors.ENDC}")
                """ to get label name for server """
                #global images
                if song in images.keys():
                    images[song].append(songList[0])
            print("\n")
    elif opType == "artist":
        for artist, songList in artistProcessed.items():
            print(f"{bcolors.OKBLUE}{bcolors.BOLD}{bcolors.UNDERLINE}---------------------------------"
                  + "Artist: " + artist[0].upper() + artist[1:] + f"---------------------------------{bcolors.ENDC}")
            for song in songList:
                if re.search(r"(.*)(" + artist.replace(" ", ".") + ")(.*)", song) != None:
                    match = re.search(
                        r"(.*)(" + artist.replace(" ", ".") + ")(.*)", song)
                    print(f"{bcolors.OKGREEN}" + match[1] + f"{bcolors.ENDC}" + f"{bcolors.UNDERLINE}{bcolors.RED}" +
                          match[2] + f"{bcolors.ENDC}" + f"{bcolors.OKGREEN}" + match[3] + f"{bcolors.ENDC}")
                """ to get label name for server """
                if song in images.keys():
                    images[song].append(songList[0])
            print("\n")
    copyImages()
    if runServerOrNot:
        runServer(images.items())
        # x = threading.Thread(target=runServer, args=(images.items(),))
        # x.start()
    runServerOrNot = False


def cleaner(directoryFile):
    for file in directories:
        if(file not in notToDeleteItems):
            fPlusDirectory = os.path.join(
                directoryFile, file).replace("\n", "")
            if os.name != "nt":
                try:
                    os.system("sudo rm -r " + "'" + fPlusDirectory + "'")
                except:
                    pass
            else:
                try:
                    os.system('rmdir /s /q "' + fPlusDirectory + '"')
                except:
                    pass


def run():
    colorama.init()
    global createdDirectories
    global directories
    global artistProcessed
    global labelsProcessed
    global runServerOrNot
    for file in createdDirectories:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}- - -  Inside " +
              file + f" that matched with your configuration  - - -{bcolors.ENDC}\n")
        try:
            directories = listDirectories(file)
            sortByLabel(file)
            sortByArtist(file)
            runServerOrNot = True
            # shutdown_server()
            decision = input(
                "Do you wanna remove all non-displayed songs from " + file + "?")

            if (decision.lower() == 'yes' or decision.lower() == 'y'):
                cleaner(file)
            else:
                print("Nothing will be removed from: " + file)
            artistProcessed = {}
            labelsProcessed = {}
        except Exception as e:
            print("This directory doesn't exist! (" + file + ")" + str(e))

    # let's clean imported images
    for image in images.values():
        if os.name != "nt":
            try:
                if image[0] != "":
                    os.system("sudo rm " + "'static/" +
                              os.path.basename(image[0]) + "'")
            except:
                pass
        else:
            try:
                if image[0] != "":
                    os.system('del /f "static\\' +
                              os.path.basename(image[0]) + '"')
            except:
                pass


def getMeta(directoryFile):
    global images
    global toKeepAlbums
    for album in notToDeleteItems:
        fPlusDirectory = os.path.join(
            directoryFile, album).replace("\n", "")
        toKeepAlbums.append(fPlusDirectory)
    for goodAlbum in toKeepAlbums:
        try:
            filesInsideAlbum = listDirectories(goodAlbum)
            for file in filesInsideAlbum:
                if "jpg" in file or "jpeg" in file or "png" in file:
                    images[os.path.basename(goodAlbum)] = [
                        os.path.join(
                            goodAlbum, file).replace("\n", "")]
                    break
                images[os.path.basename(goodAlbum)] = [
                    ""]
        except Exception as e:
            pass


def copyImages():
    for key, value in images.items():
        try:
            copy(
                value[0], "static/")
        except Exception as e:
            pass


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def runServer(dicti):
    app = flask.Flask(__name__)

    @app.route('/', methods=['GET'])
    def index():
        valor = request.args.get("id")
        albumContent = str()
        # we check if there is a cover art, if not we put a default one
        defaultCover = ""
        for album, dictList in dicti:
            defaultCover = ""
            if dictList[0] == "":
                defaultCover = "default.png"
            try:
                match = re.search(r"([\d\w\D]*)-([\d\w]*$)", album)
                albumContent = albumContent + " <tr><td> " + match[1].replace("_", " ") + " </td><td>" + \
                    dictList[1] + "</td><td>" + match[2] + "</td><td> <img src = '/static/" + \
                    os.path.basename(
                        dictList[0]) + defaultCover + "' width=400 height=400/></td></tr> "
            except Exception as e:
                pass
        return """
    <!DOCTYPE html>
    <html lang = "en">

    <head>
        <meta charset = "UTF-8">
        <title>Album Filter</title>
        <link rel = "stylesheet" href = "https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css">
    </head>

    <body>
        <style>
        h1 {
            font-size: 30px;
            color: #fff;
            text-transform: uppercase;
            font-weight: 300;
            text-align: center;
            margin: 15px;
        }

        table {
            width: 100%;
            table-layout: fixed;
        }

        .tbl-header {
            background-color: rgba(255, 255, 255, 0.3);
        }

        .tbl-content {
            height: 50em;
            overflow-x: auto;
            margin-top: 0px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        th {
            padding: 20px 15px;
            text-align: center;
            font-weight: 500;
            font-size: 35px;
            color: #fff;
            text-transform: uppercase;
        }

        td {
            padding: 15px;
            text-align: center;
            vertical-align: middle;
            font-weight: 300;
            font-size: 34px;
            color: #fff;
            border-bottom: solid 20px rgba(255, 255, 255, 0.3);
        }


        /* demo styles */

        @import url(https://fonts.googleapis.com/css?family=Roboto:400,500,300,700);

        body {
            background: -webkit-linear-gradient(left, #25c481, #25b7c4);
            background: linear-gradient(to right, #25c481, #25b7c4);
            font-family: 'Roboto', sans-serif;
        }

        section {
            margin: 50px;
            height: 800px;
        }


        /* follow me template */
        .made-with-love {
            margin-top: 40px;
            padding: 10px;
            clear: left;
            text-align: center;
            font-size: 10px;
            font-family: arial;
            color: #fff;
        }

        .made-with-love i {
            font-style: normal;
            color: #F50057;
            font-size: 14px;
            position: relative;
            top: 2px;
        }

        .made-with-love a {
            color: #fff;
            text-decoration: none;
        }

        .made-with-love a:hover {
            text-decoration: underline;
        }


        /* for custom scrollbar for webkit browser*/

        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
        }

        ::-webkit-scrollbar-thumb {
            -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
        }
    </style>

        <!-- partial: index.partial.html - ->
        <section>
            <!--for demo wrap-->
            <h1>Album Filter</h1>
            <div class="tbl-header">
                <table cellpadding="0" cellspacing="0" border=0>
                    <thead>
                        <tr>
                            <th> Album </th>
                            <th> Label </th>
                            <th> Group </th>
                            <th> Cover </th>
                        </tr>
                    </thead>
                </table>
            </div>
            <div class="tbl-content">
                <table cellpadding="0" cellspacing="0" border="0">
                    <tbody>
                        """ + albumContent + """

                        
                    </tbody>
                </table>
            </div>
        </section>
        <!-- partial - ->
        <script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'> </script>
        <script src="./script.js"> </script>

    </body>

    </html>
        """

    app.run(port=8500, use_reloader=False)


# SEQUENCE
importLabels()
importArtists()
listDirectoriesInside()
run()
