# Davinci Resolve Scripts
This repository for hopefully useful scripts for Davinci Resolve:

##ClipStock.py: This script was written to help grab sections of video clips for uploading to stock video sites.  Most sites require 30-60 second clips of video.  This is how I use this script:
  1. load all my new video clips into the media library of Davinci Resolve.
  2. add the clips to a generic timeline.
  3. play through the video
  4. As I notice interesting parts of the video, I pause the player and click F4 (the defined key I use to trigger the script).  This adds a new clip (GREEN duration marker) starting at the location of the play head including the next 30 seconds to the smart bin I have setup.
  5. The script also puts a (RED)duration marker on the timeline, which shows you the portion of the clip that was selected.  Normally you can’t see the markers placed on the clip files in the timeline. 
  6. Continue viewing the clips until you’re through the first run.
  7. Once the first run through is complete, go to the smart bin, grab all of the clips and add them to a new timeline.  At this point you can edit them, do color corrections, etc. 
  8. After all the corrections and editing is complete go to the deliver tab and render individual clips from the timeline. 	 
  
  Here is what the script does when you execute it:
  1. Based on the current location of the play head in the timeline, it places a duration marker on the current clip with a default length of 30 seconds.  It puts the word STOCK in the notes of the marker so these markers can be sorted into a Smart Bin.
  2. It also places a duration marker in the same place on the timeline; this gives a visual representation of the beginning and end of the marked clip on the timeline.
	   
  **Note:** If the length of the clip is less than the length of the duration marker, the marker is placed from the current location to the end of the current clip.   If you’re getting clips that are shorter than what you expected it's likely because it ran into the end of the clip.

  To create the Smart Bin that will show the duration markers on the clips do the following in Davinci Resolve:
  1. In the lower left-hand corner of DR where is says “User Smart Bins”.  Left click “User Smart Bins”, and choose to add a Smart Bin.
  2. Name:  Stock Clips
  3. [CHECK]View in all Projects
  3. Match Any
  4. Match:
		  MediaPool Properties
		  Marker Notes
		  Contains
		  STOCK




