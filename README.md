# univid
Quick python script to view motion events created by ubiquiti cameras from a local backup.

On first startup univid will ask you to input the location of your videos directory. Please input the full path.
This assumes you are backing up the /srv/unifi-video/videos directory and keeping the default directory/file structure.
univid will not ask you the location of this directory again. To change, simply edit the .univid file in your /home.

When univid is run it will search for motion events in the directory you named above and list them in order of start time.
By default univid only gathers events from the past 24 hours. This can be changed, see univid.py -h for more information.
To select an event simply enter the event number and press enter. You can also enter several videos by listing the
event numbers seperated by a space or a comma. You can also enter a range of videos using the "-" char, like this: 2-5.
An "*" will play all events in the list.

While in the selection screen pressing "h" will bring up a help message. "r" or enter with no argument will refresh the list.
"q" will quit the program.
