#!/usr/bin/env python3
import os
import sys
import csv
import re

labels = list()
artists = list()
directories = list()
createdDirectories = set()
rootDirectory = str()
labelsProcessed = dict()
artistProcessed = dict()
notToDeleteItems = set()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\33[91m'
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


def sortByLabel():
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
    formatter("label")


def sortByArtist():
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
    formatter("artist")


def formatter(opType):
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
            print("\n")


def cleaner(directoryFile):
    for file in directories:
        if(file not in notToDeleteItems):
            fPlusDirectory = os.path.join(
                directoryFile, file).replace("\n", "")
            os.system("sudo rm -r " + "'" + fPlusDirectory + "'")


# SEQUENCE
importLabels()
importArtists()

listDirectoriesInside()
for file in createdDirectories:
    print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}- - -  Inside " +
          file + f" that matched with your configuration  - - -{bcolors.ENDC}\n")
    try:
        directories = listDirectories(file)
        sortByLabel()
        sortByArtist()
        decision = input(
            "Do you wanna remove all non-displayed songs from " + file + "?")
        if (decision.lower() == 'yes' or decision.lower() == 'y'):
            cleaner(file)
        else:
            print("Nothing will be removed from: " + file)
        artistProcessed = {}
        labelsProcessed = {}
    except:
        print("This directory doesn't exist!")
