#!/usr/bin/env python3

###############################################################################################################################
# ClipStock.py [duration]
#   Duration = the number of seconds to use for the length of the duration marker, caviot - the clip length will determine the
#   length of the marker if the clip from play head to end is less than the requested number of seconds.
#
# Debug:  True/False, turn on or off debug statements
# default_len:  This is the default length of clip that will be used if no argument is given to the script.
###############################################################################################################################

import sys
import os
sys.path.append("C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules/")
import DaVinciResolveScript as dvr
import time


####
# Conversion Functions
####

##
# Convert Timecode to Frames
#
# timecode_to_frames(tc, fps, is_drop_frame=False)
# 
# tc = timecode in the format: HH:MM:SS:FF 
# fps = frames per seconds
# is_drop_frame = {True/False} 
#   if True = Drop 2 Frames every Minute, Except the 10th minute.
#   if False = Dont Drop Frames (Default)
#
# return number_of_frames
##
def timecode_to_frames(tc, fps, is_drop_frame=False):
    # Standardize separator and split
    parts = list(map(int, tc.replace(';', ':').split(':')))
    hh, mm, ss, ff = parts
    
    # We use the rounded FPS for base calculations (e.g., 29.97 -> 30)
    base_fps = round(fps)
    
    total_minutes = (60 * hh) + mm
    total_frames = ((hh * 3600) + (mm * 60) + ss) * base_fps + ff

    if is_drop_frame:
        # Drop 2 frames every minute, except every 10th minute
        drop_frames = 2 * (total_minutes - (total_minutes // 10))
        total_frames -= drop_frames
        
    return total_frames

##
# Convert frames to Timecode
#
# frames_to_timeccode(total_frames, fps, is_drop_frame=False):
# 
# frames = number of frames to convert to timecode 
# fps = frames per seconds
# is_drop_frame = {True/False} 
#   if True = Drop 2 Frames every Minute, Except the 10th minute.
#   if False = Dont Drop Frames (Default)
#
# Return Timecode in the format: HH:MM:SS:FF
##
def frames_to_timecode(total_frames, fps, is_drop_frame=False):
    base_fps = round(fps)
    sep = ":"

    if is_drop_frame:
        sep = ";"
        # 17982 is the frames in 10 mins of 29.97 DF ((10*60*30) - 18)
        d = total_frames // 17982
        m = total_frames % 17982
        
        # Adjustment for the "skipped" numbers
        total_frames += (18 * d) + (2 * ((m - 2) // 1798)) if m > 2 else (18 * d)

    ff = total_frames % base_fps
    ss = (total_frames // base_fps) % 60
    mm = (total_frames // (base_fps * 60)) % 60
    hh = (total_frames // (base_fps * 3600))

    return f"{hh:02}:{mm:02}:{ss:02}{sep}{ff:02}"



#########
# Main 
#########

Debug = True
default_len = 30

#########
# Python Script Arguments:
#
# arg #1:  length of clip in Seconds - note the clip will be this length or to the end of the clip which ever is shorter.
#########

### 
# Initialize Resolve
###
resolve = dvr.scriptapp('Resolve')                              # create resolve object
ver = resolve.GetVersion()                                      # Davinci Resolve Version


# ==============
# Parse Arguments
# ==============

n = len(sys.argv)
if n > 1:
  clip_len = int(sys.argv[1])
else:
  clip_len = default_len

if Debug:
  print("\n\n\n")  
  print("===========================================================")
  print(" ", resolve.GetProductName())
  print(f"  Version: {ver[0]}.{ver[1]}.{ver[2]} build {ver[3]} {ver[4]}")
  print("  Current Page:", resolve.GetCurrentPage().capitalize(), "\n")  
  
  print("  This script finds the video clip that is under the playhead, and calculates an offset to that clip.")
  print("  It then places a duration marker on the clip not the timeline (duration of the marker can be set my argument")
  print("  to the acript of the default od 30seconds.  These markers can be used to copy clips into a timeline and") 
  print("  then for export to stock clips.") 
  print(" ")  
  print(" ", sys.argv[0].rstrip())
  print(" ")  
  print("  Written by Geoff Kuchera and others ")  
  print("===========================================================\n")
  

### 
# Setup initial objects and variables required for the script
###
projectManager = resolve.GetProjectManager()                    # create project manager object
project = projectManager.GetCurrentProject()                    # create project object
mediaPool = project.GetMediaPool()                              # create media pool object 
root_bin = mediaPool.GetRootFolder()                            # locate the root media pool folder
tl = project.GetCurrentTimeline()                               # create a timeline object from the current timeline
framerate = tl.GetSetting("timelineFrameRate")                  # get project frame rate

StFr = tl.GetStartFrame()                                       # Timeline Start Frame # 
TcSt = frames_to_timecode(tl.GetStartFrame(), framerate)        # Timeline Start Timecode
EnFr = tl.GetEndFrame()                                         # Timeline End Frame #
TcEn = frames_to_timecode(tl.GetEndFrame(), framerate)          # Timeline End Timecode
CrFr = timecode_to_frames(tl.GetCurrentTimecode(),framerate)    # Timeline Play Head Current Position Frame #
TcCr = tl.GetCurrentTimecode()                                  # Timeline Play Head Current Position Timecode

if Debug:
  print("\n= TIMELINE ===============================================\n")
  print("  Timeline Name:            ", tl.GetName()) 
  print("  Begining of the Timeline: ", TcSt, "  Frame:  ", StFr)
  print("  Last Frame in Timeline:   ", TcEn, "  Frame:  ", EnFr)
  print("  Current Timecode:         ", TcCr, "  Frame:  ", CrFr)


current_clip = tl.GetCurrentVideoItem()                             # Create a current_video_item object from the current timeline
current_clip_offset = current_clip.GetStart()                       # Find the start frame of the current clip
name, extension = os.path.splitext(current_clip.GetName())          # return the Name and Extension of the current clip

ClTlStTc = frames_to_timecode(current_clip.GetStart(),framerate)    # Timeline clip start Timecode    
ClTlStFr = current_clip.GetStart()                                  # Timeline clip start Frame #                                  
ClStTc = frames_to_timecode(0,framerate)                            # Clip starting timecode
ClStFr = 0                                                          # clip start frame number = always 0

ClTlEnTc = frames_to_timecode(current_clip.GetEnd(),framerate)      # Timeline End of clip timecode
ClTlEnFr = current_clip.GetEnd()                                    # Timeline End of clip Frame #
ClEnTc   = frames_to_timecode((current_clip.GetEnd() - current_clip_offset),framerate)  # Clip end timecode
ClEnFr   = current_clip.GetEnd() - current_clip_offset              # Clip End frame #

ClCrTc = frames_to_timecode(CrFr - current_clip_offset,framerate)   # Clip current location timecode
ClCrFr = CrFr - current_clip_offset                                 # Clip current location Frame #

if Debug: 
  print("\n= Current CLIP ===========================================\n")
  print("  Clip Name:                ", name, extension)
  print("")
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Description","TL Timecode","TL Frames","CL Timecode", "CL Frames"))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("--------------","-------------","-------------","-------------", "-------------"))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip Start",ClTlStTc,ClTlStFr,ClStTc, ClStFr))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip End",ClTlEnTc,ClTlEnFr,ClEnTc,ClEnFr))  
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip playhead",TcCr, CrFr, ClCrTc, ClCrFr))


###
# -- Media clip Marker 
#
#  Create the Media clip marker - this is what is used to actually act as the clip duration marker, that is later used to create the 
#  exported clips for stock.  
### 
mp_item = current_clip.GetMediaPoolItem()                           # Create a media pool object from the current clip.  
frames_req  = int(framerate * clip_len)                             # Calculate the number of requested frames from the duration and Framerate.
frames_left = int((current_clip.GetEnd() - current_clip_offset) - (CrFr - current_clip_offset))     # Find the number of frames left in the clip
marker_frame = int(CrFr - current_clip.GetStart())                  # Use frame offset into the current clip as part of the marker name.
marker_color = "Green"                                              # color the marker Green on the close
marker_note = "STOCK"                                               # put a note in the Marker of "STOCK" that can be used to trigger a smart bin to collect it.
marker_duration = current_clip.GetDuration() - marker_frame         # length of the marker will either be the duration * framerate or the length of the rest of the clip * framerate.
marker_name = name +" offset " + str(CrFr - current_clip_offset) + " frames"    # Name to add to the marker 


###
#   Determine if there are enough frames left in the clip to provide the requested length, if not use the length of the clip
###
if frames_req > frames_left:
   marker_duration = frames_left
else:
   marker_duration = frames_req


if Debug:   
  print("\n= DURATION MARKER - CLIP =================================\n")
  print("  Clip length Requested:    ", clip_len, "Seconds /", int(clip_len * framerate),"frames @", framerate, "fps")
  print("  Marker Name:       ", marker_name)
  print("  Marker Color:      ", marker_color)
  print("  Marker Frame:      ", marker_frame)
  print("  Marker Note:       ", marker_note)
  print("  Frames Requested:  ", frames_req)
  print("  Frames Left:       ", frames_left)  
  print("  Marker Duration:   ", marker_duration)
   

if mp_item:
  mp_item.AddMarker(marker_frame,marker_color,marker_name,marker_note, marker_duration, "")
  if Debug:
    print(f"\n  Duration marker added to clip '{current_clip.GetName()}' at frame {marker_frame}")
else:
  if Debug:
    print("\n  Could not retrieve Media Pool Item for the selected clip.")  


###
# --  Timeline Marker
#
#  Create a Media timeline duration marker to show that the there has been a stock pick done at this location on the timeline.
###

cl_marker_frame = marker_frame                                          # Timeline Marker frame
cl_marker_color = "Blue"                                                 # Set the Timeline Marker to color Red
cl_marker_note = "Stock"                                                # add the Note "Stock" to the timeline Marker.
cl_marker_duration = marker_duration                                    # Marker Duration for the timeline Marker
cl_marker_name = tl.GetName() +" offset " + str(CrFr) + " frames"       # Setup the marker name


if Debug:
  print("\n= DURATION MARKER - TimeLine Clip =============================\n")
  print("  CL_Marker Name:       ", cl_marker_name)
  print("  CL_Marker Color:      ", cl_marker_color)
  print("  CL_marker_frame:      ", cl_marker_frame)
  print("  CL_Marker Note:       ", cl_marker_note)
  print("  CL_Current_Frame:     ", CrFr)
  print("  CL Marker Duration:   ", cl_marker_duration)

if current_clip:
  current_clip.AddMarker(cl_marker_frame,cl_marker_color,cl_marker_name,cl_marker_note, cl_marker_duration, "")
  if Debug:
    print(f"\n  Duration marker added to clip '{current_clip.GetName()}' at frame {cl_marker_frame}")
else:
  if Debug:
    print("\n  Could not retrieve Media Pool Item for the selected clip.")




tl_marker_frame = CrFr - StFr                                                  # Timeline Marker frame
tl_marker_color = "Red"                                                 # Set the Timeline Marker to color Red
tl_marker_note = "Stock"                                                # add the Note "Stock" to the timeline Marker.
tl_marker_duration = marker_duration                                    # Marker Duration for the timeline Marker
tl_marker_name = tl.GetName() +" offset " + str(CrFr) + " frames"       # Setup the marker name

if Debug:
  print("\n= DURATION MARKER - TimeLine =============================\n")
  print("  TL_Marker Name:       ", tl_marker_name)
  print("  TL_Marker Color:      ", tl_marker_color)
  print("  TL_marker_frame:      ", tl_marker_frame)
  print("  TL_Marker Note:       ", tl_marker_note)
  print("  TL_Current_Frame:     ", CrFr)
  print("  TL Marker Duration:   ", tl_marker_duration)

if current_clip:
  tl.AddMarker(tl_marker_frame,tl_marker_color,tl_marker_name,tl_marker_note, tl_marker_duration, "")
  if Debug:
    print(f"\n  Duration marker added to clip '{current_clip.GetName()}' at frame {tl_marker_frame}")
else:
  if Debug:
    print("\n  Could not retrieve Media Pool Item for the selected clip.")


    
clmkrs = mp_item.GetMarkers()
tlmkrs = tl.GetMarkers()

 
if Debug:
  print("\n  Markers on Current Clip:  ")
  for clip_id, details in clmkrs.items():
      print(f"  ID: {clip_id}")
      for key, value in details.items():
          # Using .capitalize() to make the output look like a label
          print(f"    {key.capitalize()}: {value}")

  print("\n\n  Markers on Timeline:  ")
  for clip_id, details in tlmkrs.items():
      print(f"  ID: {clip_id}")
      for key, value in details.items():
          # Using .capitalize() to make the output look like a label
          print(f"    {key.capitalize()}: {value}")


exit(True)