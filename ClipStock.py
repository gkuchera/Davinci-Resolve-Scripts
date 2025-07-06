import sys
import os
sys.path.append("C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules/")
import DaVinciResolveScript as dvr
import time

def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
        return sum(f * float(t) for f,t in _zip_ft)
    elif isinstance(value, (int, float)):  # frames
        return value / framerate
    else:
        return 0

def _timecode(seconds):
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
            .format(h=int(seconds/3600),
                    m=int(seconds/60%60),
                    s=int(seconds%60),
                    f=round((seconds-int(seconds))*framerate))

def _frames(seconds):
    return seconds * framerate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def frames_to_timecode(frames, start=None):
    return _timecode(_seconds(frames) + _seconds(start))


#########
# Main 
#
# ClipStock.py [duration]
#   Duration = the number of seconds to use for the length of the duration marker, caviot - the clip length will determine the
#   length of the marker if the clip from play head to end is less than the requested number of seconds.
#
# Debug:  True/False, turn on or off debug statements
# default_len:  This is the default length of clip that will be used if no argument is given to the script.
#########

Debug = True
default_len = 30

#########
# Python Script Arguments:
#
# arg #1:  length of clip in Seconds - note the clip will be this length or to the end of the clip.
#########


# ==============
# Parse Arguments
# ==============

n = len(sys.argv)
if n > 1:
  clip_len = int(sys.argv[1])
else:
  clip_len = default_len

if Debug:
  print("\n")
  print("****************************************************")
  print("* ")
  print("* ", sys.argv[0].rstrip(), "- DaVinci Resolve Script")
  print("*")
  print("*  This script finds the video clip that is under the playhead, and calculates an offset to that clip.")
  print("*  It then places a duration marker on the clip not the timeline (duration of the marker can be set my argument")
  print("*  to the acript of the default od 30seconds.  These markers can be used to copy clips into a timeline and") 
  print("*  then for export to stock clips.")
  print("*")
  print("*   Written by Geoff Kuchera and others ")
  print("* ")
  print("****************************************************")
  

# Initialize Resolve

resolve = dvr.scriptapp('Resolve')
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
mediaPool = project.GetMediaPool()
root_bin = mediaPool.GetRootFolder()
tl = project.GetCurrentTimeline()

# Get current playhead position and calculate 30 seconds ahead

curr_tc = tl.GetCurrentTimecode()
framerate = tl.GetSetting("timelineFrameRate")
curr_frame = int(timecode_to_frames(curr_tc))


if Debug:
  print("\n= TIMELINE ===============================================\n")
  print("  Timeline Name:            ", tl.GetName())
  print("  Begining of the Timeline: ", frames_to_timecode(tl.GetStartFrame()),"  Frame:  ",tl.GetStartFrame() )
  print("  last Frame in Timeline:   ", frames_to_timecode(tl.GetEndFrame()),  "  Frame:  ",tl.GetEndFrame() )
  print("  Current Timecode:         ", curr_tc, "  Frame:  ",curr_frame)
  
end_frame = int(curr_frame + (clip_len * framerate))
end_tc = frames_to_timecode(end_frame)
current_clip = tl.GetCurrentVideoItem()
current_clip_offset = current_clip.GetStart()
name, extension = os.path.splitext(current_clip.GetName())

if Debug: 
  print("\n= Current CLIP ===========================================\n")
  print("  Clip Name:                ", name, "  Type: ", extension)
  print("  Clip length Requested:    ", clip_len, "Seconds /", int(clip_len * framerate),"frames @", framerate, "fps")
  
  print("")
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Description","TL Timecode","TL Frames","CL Timecode", "CL Frames"))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("--------------","-------------","-------------","-------------", "-------------"))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip Start",frames_to_timecode(current_clip.GetStart()),current_clip.GetStart(),frames_to_timecode(0),0))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip playhead",curr_tc,curr_frame,frames_to_timecode(curr_frame - current_clip_offset),curr_frame - current_clip_offset))
  print("  %-15s %-14s %-14s %-14s %-14s" % ("Clip End",frames_to_timecode(current_clip.GetEnd()),current_clip.GetEnd(),frames_to_timecode((current_clip.GetEnd() - current_clip_offset)), (current_clip.GetEnd() - current_clip_offset)))  


mp_item = current_clip.GetMediaPoolItem()  
frames_req  = int(framerate * clip_len)
frames_left = int((current_clip.GetEnd() - current_clip_offset) - (curr_frame - current_clip_offset))
marker_frame = int(curr_frame - current_clip.GetStart())
marker_color = "Green"
marker_note = "STOCK"
marker_duration = current_clip.GetDuration() - marker_frame
marker_name = name +" offset " + str(curr_frame - current_clip_offset) + " frames"


if frames_req > frames_left:
   marker_duration = frames_left
else:
   marker_duration = frames_req
   

if Debug:
  print("\n= DURATION MARKER - CLIP =================================\n")
  print("  Marker Name:       ", marker_name)
  print("  Marker Color:      ", marker_color)
  print("  Marker Frame:      ", marker_frame)
  print("  Marker Note:       ", marker_note)
  
if Debug:
  print("  Frames Requested:  ", frames_req)
  print("  Frames Left:       ", frames_left)  
  print("    Marker Duration: ", marker_duration)
   

if mp_item:
  mp_item.AddMarker(marker_frame,marker_color,marker_name,marker_note, marker_duration, "")
  if Debug:
    print(f"\n  Duration marker added to clip '{current_clip.GetName()}' at frame {marker_frame}")
else:
  if Debug:
    print("\n  Could not retrieve Media Pool Item for the selected clip.")  


tl_marker_frame = marker_frame
tl_marker_color = "Red"
tl_marker_note = "Stock"
tl_marker_duration = marker_duration
tl_marker_name = tl.GetName() +" offset " + str(tl_marker_frame) + " frames"

if Debug:
  print("\n= DURATION MARKER - TimeLine =============================\n")
  print("  TL_Marker Name:       ", tl_marker_name)
  print("  TL_Marker Color:      ", tl_marker_color)
  print("  TL_marker_frame:      ", tl_marker_frame)
  print("  TL_Marker Note:       ", tl_marker_note)
  print("  TL_Current_Frame:     ", curr_frame)
  print("  TL Marker Duration:   ", tl_marker_duration)

if current_clip:
  #current_clip.AddMarker(marker_frame,marker_color,marker_name,marker_note, marker_duration, "")
  current_clip.AddMarker(tl_marker_frame,tl_marker_color,tl_marker_name,tl_marker_note, tl_marker_duration, "")
  if Debug:
    print(f"\n  Duration marker added to clip '{current_clip.GetName()}' at frame {tl_marker_frame}")
else:
  if Debug:
    print("\n  Could not retrieve Media Pool Item for the selected clip.")

    
if Debug:
  print("\n  Markers on Current Clip:  ",mp_item.GetMarkers())
  print("\n  Markers on Timeline:  ",current_clip.GetMarkers())


exit(True)



