"""
    a Simple script that deletes all PNG files in the directory
    Used to clean out directories while testing the Radio Plotting Script
    2024/01/26 Resbi & RJGamesAhoy
"""

import os, sys

def deleteFiles(fileList):
    for file in fileList:
        os.remove(os.getcwd() + '/Output/' + file)
    return

def scanForPng():
    toDelete = []
    currentDirectory = str(os.getcwd())
    for file in os.listdir(currentDirectory + '/Output/'):
        if ".png" in file:
            toDelete.append(file)
    if toDelete == []:
        print("There are no PNG's in this Directory\nExiting")
        sys.exit(0)
    return toDelete


def main():
    print("Deleting all PNG files in " + str(os.getcwd() + '/Output/'))
    filesToDelete = scanForPng()
    deleteFiles(filesToDelete)
    print("All Done!")
    return

main()