#!/bin/env python

# view motion events from ubiquiti cameras

import json, os, datetime, time, argparse, subprocess, sys

configPath = os.path.join('/', 'home', os.uname()[1], '.univid')
jsonFiles = {}
events = {}
helpString = '''
Type the number of an event to play it.
You can select a range of events like this: 10-12 (reverse order also works: 12-10)
You can select several videos if you separate them with a "," or space like this: 3,5,7 (or) 3 5 7
* will play all videos
q will quit
r will refresh the list (or just hit enter)
h show this help

Press enter to continue.'''


def humanTime(timestamp):
    timestamp = float(timestamp / 1000)
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def getJsonFiles():
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if ".json" in filename:
                jsonFiles[os.path.join(dirpath, filename)] = dirpath.split('/')[1]


def getVidFiles(startTime, endTime, camera, cameraName):
    vidList = []
    eventName = '''{0} {1}'''.format(humanTime(startTime), cameraName)
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if ".mp4" in filename and camera in dirpath:
                fileStart = int(filename.split('_')[0])
                fileEnd = int(filename.split('_')[1])
                if fileStart >= startTime and fileEnd <= endTime:
                    vidList.append(os.path.join(dirpath, filename))

    vidList.sort()
    events[eventName] = vidList


def getEvents(days, hours):
    startTime = 0
    endTime = 0
    if hours != 0:
        maxAge = time.time() - 3600 * hours
    else:
        maxAge = time.time() - 86400 * days

    for filePath, camera in jsonFiles.items():
        with open(filePath, 'r') as f:
            data = json.loads(f.read())
            for key, value in data.items():
                if key == "startTime":
                    startTime = value
                if key == "endTime":
                    endTime = value
                if key == "meta":
                    for k, v in value.items():
                        if "cameraName" in k:
                            cameraName = v

            if (startTime / 1000) > maxAge:
                getVidFiles(startTime, endTime, camera, cameraName)


def checkRange(maxNum, num):
    if int(num) > maxNum or int(num) < 0:
        input('\nValue out of range: {0} Press enter to continue\n'.format(num))
        return 1


def main():
    parser = argparse.ArgumentParser(description='List and view events local backup of unifi-video system.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', metavar='<n>', type=int, default=1, help='List last <n> days of events.')
    parser.add_argument('-t', metavar='<n>', type=int, default=0, help='List last <n> hours of events.')
    args = parser.parse_args()

    # setup
    if os.path.isfile(configPath) is False:
        vidPath = input('No config found, please enter the full path to your "videos" directory:\n')
        if os.path.isdir(vidPath) is False:
            print("Error: {0} does not exist")
        with open(configPath, 'w') as f:
            f.write(vidPath)
    else:
        with open(configPath, 'r') as f:
            vidPath = f.read()

    os.chdir(vidPath)
    getJsonFiles()
    getEvents(args.d, args.t)

    # main loop
    while True:
        vidFiles = []
        eventNumber = 0
        for event, files in sorted(events.items()):
            eventNumber += 1
            print(eventNumber, event)

        selected = input("\nSelect an event to view (h for help):\n")
        if "q" in selected:
            sys.exit()
        elif "r" in selected:
            continue
        elif "h" in selected:
            input(helpString)
            continue
        elif "*" in selected:
            for x in range(0, eventNumber):
                vidFiles.append(' '.join(events[sorted(events)[x - 1]]))
        elif selected is "":
            continue
        elif not any(char.isdigit() for char in selected):
            input("\nInvalid input\n")
            continue
        elif "-" in selected:
            first = int(selected.split('-')[0])
            last = int(selected.split('-')[1])
            if checkRange(eventNumber, first) or checkRange(eventNumber, last):
                continue

            if first < last:
                for x in range(first, last + 1):
                    vidFiles.append(' '.join(events[sorted(events)[x - 1]]))
            else:
                for x in range(first, last - 1, -1):
                    vidFiles.append(' '.join(events[sorted(events)[x - 1]]))
        elif "," in selected:
            selectedList = selected.split(',')
            if any(checkRange(eventNumber, i) for i in selectedList):
                continue

            for x in selectedList:
                vidFiles.append(' '.join(events[sorted(events)[int(x) - 1]]))
        elif " " in selected:
            selectedList = selected.split(' ')
            if any(checkRange(eventNumber, i) for i in selectedList):
                continue

            for x in selectedList:
                vidFiles.append(' '.join(events[sorted(events)[int(x) - 1]]))
        else:
            if checkRange(eventNumber, selected):
                continue
            vidFiles = events[sorted(events)[int(selected) - 1]]

        subprocess.call('mpv' + ' ' + ' '.join(vidFiles), shell=True)


if __name__ == "__main__":
    main()
