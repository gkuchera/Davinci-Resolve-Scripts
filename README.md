# Davinci Resolve Scripts

This repository for hopefully usefull scripts for Davinci Resolve:

ClipStock.py:  This script was written to help grab sections of video clips for uploading to stock video sites.
  Most sites require 30-60second clips of video.  This is how i use this script:
  
  1. load all my new video clips into the media library of Davinci Resolve.
  2. add  the clips to a generaic timeline.
  3. play through the video
  4. as i see interesting pieces of video i pause the player and click F4 (the defined key i use for the script).  
       This adds a new clip starting at the locatio of the play head including the next 30 seconds to the smart 
	   bin I have setup.
  5. the script also puts a duration marker on the timeline so visually i can see the length of the clip.
  6. i continue viewing the clips until i'm through the first run.
  7. one the first run through it complete, i go to the smart bin, grab all of the clips and add them to a new timeline.
       I can then edit them as i see fit, do color corrections, etc. 
  8. Then i go to the deliver tab and render individual clips from the timeline. 	 
  
  
Here is what the script does everytime you execute it:
  1. Based on the current location of the play head in the timeline, it places a duration marker on the current clip with a 
       default length of 30 seconds.  It puts the word STOCK in the notes of the marker so these markers can be sorted into a 
	   Smart Bin.
  2. It also places a duration marker in the same place on the timeline, this gives a visual representation of the beginning
       and end of the marked clip on the timeline.
	   
  Note: If the length of the clip is less than the length of the duration marker, the marker is placed from the current 
       location to the end of the current clip.   So if your getting clips shorter than what you wanted it's likley because 
	   it ran into the end of the clip.

To create the Smart Bin that will show the duration markers on the clips do the following in Davinci Resolve:

  1. In the lower left hand corner of DR where is says user Smart Bins.  Left click User Smart Bins, and choose add Smart Bin.
  2. Name:  Stock Clips
  3. Match:
		  MediaPool Properties
		  Marker Notes
		  Contains
		  STOCK
  



