from pytube import YouTube
from pytube import Playlist
from pydub import AudioSegment
import subprocess
import re
import string
import os
import time
import shutil
import contextlib
import wave
import math

DESTINATION = "Z:/Media/Music"

class Downloader:
   

    #yt.streams.filter(progressive=False,type="audio").order_by("abr").last().download()

    def __init__(self, url='https://www.youtube.com/watch?v=u7AG8pLM2fc'):
        self.update_url(url)

    def update_url(self, url):
        self.yt = YouTube(url,
                          on_complete_callback=on_download_finish,
                          use_oauth=True,
                          allow_oauth_cache=True
                          )

    def download(self,prog=False, ext="mp4",order_by="abr"):
        self.yt.streams.filter(progressive=prog, file_extension=ext).order_by(order_by).first().download()

def filter_string(input_string) -> str:
        
        allowed_characters = string.ascii_letters + string.digits + string.whitespace + "\"#$%&'()*+,-.:;<=>@[\\]^_`{|}~"
        pattern = f"[^{re.escape(allowed_characters)}]"
    
        return re.sub(pattern, '', input_string)    


def convert_to_wav(file, title) -> str:
        
        new_title = f'{filter_string(title)}.wav'


        print(title)
        subprocess.call(['ffmpeg', '-i', file, new_title])
        print(f"{new_title} converted")

        return new_title

def on_download_finish(stream, path):

    wav = convert_to_wav(path, stream.title)
    resp = input(f"{stream.title} converted to wav. Is this a song or an album?\n1 = Song, 2 = Album\n")
    if resp == "1":
        new_spot = f"{DESTINATION + '/' + wav}"
        shutil.move(wav, new_spot)
    elif resp == "2":
        split_album(stream, wav)
        os.remove(wav)
    else:
        print("Try that one more time.")
        on_download_finish(stream, path)
        return
    

    os.remove(path)

def download_playlist(url : str,prog : bool = False, ext : str = "mp4", order_by : str = "abr"):
    #TODO: Roll all download funcs into one
    p = Playlist(url)
    videos = []
    dir = filter_string(p.title)
    if dir == '':
        dir = "Songs!!!!!"
    if not os.path.exists(dir):
        os.makedirs(dir)

    for video in p.videos:
        video.register_on_complete_callback(on_playlist_song_download)
        video.streams.filter(progressive=prog, file_extension=ext).order_by(order_by).first().download()
        
def on_playlist_song_download(stream, path):
    title = filter_string(stream.title)
    wav = convert_to_wav(path, title)
    os.remove(path)
    #Fuck it
    shutil.move(wav, "Album/" + wav)

def split_album(stream, fpath):
    dir = filter_string(stream.title)
    if not os.path.exists(dir):
         os.makedirs(dir)

    start_code = ""
    prev_end = "0:00"
    time_pairs = []
    loops = 0
    while start_code.lower() != "r":
        loops += 1
        print(f"Default option: {prev_end}")
        start_code = input("Please input starting timecode (leave blank for default option or r for ready): ")

        if start_code == "r":
           break
        elif start_code == "":
            timecode_start = prev_end
        else:
           timecode_start = start_code

        timecode_end = input("Please input ending timecode (leave blank for video end): ")
        if timecode_end == "":
             
             with contextlib.closing(wave.open(fpath, 'r')) as f:
                  #TODO: Fix this jank shitfest
                  #For now just enter in the end time manually
                  frames = f.getnframes()
                  rate = f.getframerate()
                  length = frames / float(rate)

                  timecode_mins = math.floor(length / 60)
                  timecode_secs = math.floor(length % 60)
                  timecode_end = f"{timecode_mins}:{timecode_secs}"

        song_title = f"{loops}. {input('Please enter song title: ')}"
        s_split = timecode_start.split(":")
        e_split = timecode_end.split(":")

        s_time = timestamp_decode(s_split)
        e_time = timestamp_decode(e_split)

        if s_time > e_time:
            #Swaps the start and end if start is a higher number
            temp = e_time
            e_time = s_time
            s_time = temp

        time_pairs.append({"start" : s_time, 
                           "end" : e_time, 
                           "title" : song_title})
        
        prev_end = timecode_end

    for song in time_pairs:
        print(fpath)
        print(song['start'])
        print(song['end'])
        segment = AudioSegment.from_wav(fpath)
        print(segment)
        segment = segment[song["start"] : song["end"]]
        segment.export(f"{dir + '/' + song['title']}.wav", format="wav")

    print("Done!")

def timestamp_decode(split : str) -> int:
    #Returns the length of a timecode in miliseconds
    if len(split) == 2:
        hours = 0
        minutes = int(split[0])
        seconds = int(split[1])
    elif len(split) == 3:
        hours = int(split[0])
        minutes = int(split[1])
        seconds = int(split[2])
    else:
        resp = input("Invalid Timestamp. Retry: ")
        return timestamp_decode(resp)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return (total_seconds * 1000)

def mainloop():

    d = Downloader("Default")
    url = "Input URL: "

    if "list" in url or "playlist" in url:
        download_playlist(url)
    else:
        d.update_url(url)


if __name__ == "__main__":
    while True:
        mainloop()
    
    #d.download()
    """
    answer = ""
    links = []
    while answer.lower() != "r":
        answer = input("Input link to download and convert (or r to signify ready): ")
        if answer.lower() != "r":
            links.append(answer) 

    for link in links:
         d.update_url(url=link)
         print(d.download())

    print("Done!")
    """