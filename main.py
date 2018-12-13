from mp3_tagger import MP3File, VERSION_1
from collections import namedtuple
from mutagen import File
import os
from pydub import AudioSegment
import requests
import json

auth = ('ines.bergmann@web.de', 'ines')

def post_artwork(doc):
    url = "http://localhost:8001/services/documents"
    r = requests.post(url,
                      auth=auth,
                      headers={'Content-Type': doc.contentType},
                      data=doc.content)
    return int(r.text) if r.status_code == 200 else 1

def post_recording(doc):
    url = "http://localhost:8001/services/documents"
    r = requests.post(url,
                      auth=auth,
                      headers={'Content-Type': doc.contentType},
                      data=doc.content)
    return int(r.text) if r.status_code == 200 else 1

def post_album(album,cover_reference):
    url = "http://localhost:8001/services/albums"
    album_template = {
        "releaseYear": album.release_year,
        "title": album.title,
        "trackCount": album.track_count
    }
    r = requests.post(url,
                      auth=auth,
                      params={ 'coverReference' : str(cover_reference)},
                      json=album_template)
    return int(r.text) if r.status_code == 200 else 1

def post_track(track,album_reference,recording_reference,owner_reference=3):
    url = "http://localhost:8001/services/tracks"
    track_template = {
        "artist" : track.artist,
        "name" : track.name,
        "genre" : track.genre,
        "ordinal" : int(track.ordinal)
    }
    params = {
        'ownerReference' : owner_reference,
        'recordingReference' : recording_reference,
        'albumReference' : album_reference,
    }
    r = requests.post(url,
                      auth=auth,
                      params=params,
                      json=track_template)
    return int(r.text) if r.status_code == 200 else 1


class Document(namedtuple("Document", "contentType content")):
    def __str__(self):
        return f'<Document contentType={self.contentType} content={str(self.content)[0:8]}>'
    def __repr__(self):
        return str(self)

class Track():
    def __init__(self,name,artist,genre,ordinal):
        self.name=name
        self.artist=artist
        self.genre=genre
        self.ordinal=ordinal

    def __repr__(self):
        return f'<Track {str(self.__dict__)}>'

Album = namedtuple("Album", "title release_year track_count")
# Assumes the following directory structure
# basedir
#   |__albumA
#      |__tracka.mp3
#      |__trackb.mp3
#   |__albumB
#      |__tracka.mp3

basedir = "./some_mp3_files/"
for dir in os.listdir(basedir):
    album = None
    artwork = None
    tracks = []
    recordings = []
    for fp in os.listdir(os.path.join(basedir,dir)):
        path_to_mp3 = os.path.abspath(os.path.join(basedir,dir,fp))
        file = File(path_to_mp3)

        # Convert audio file to Document
        recording_mime = file.mime[0]
        twenty_secs = 20 * 1000
        audio = AudioSegment.from_mp3(path_to_mp3)[:twenty_secs]
        recording_bytes = audio.export("sample.mp3")
        recording_bytes = open("sample.mp3","rb").read()
        recordings.append(Document(contentType=recording_mime, content=recording_bytes))

        # Convert tags to Track
        tags = file.tags
        try:
            artist = file.tags['TPE1'].text[0]
        except KeyError:
            artist = 'unkown'
        try:
            genre = file.tags['TCON'].text[0]
        except KeyError:
            genre = 'misc'
        try:
            name = file.tags['TIT2'].text[0]
        except KeyError:
            name = 'unkown'
        try:
            ordinal = int(file.tags['TRCK'].text[0])
        except KeyError:
            ordinal = 0
        track = Track(name=name,artist=artist,genre=genre,ordinal=ordinal)
        tracks.append(track)

        # Convert artwork tags/bytes to Data (may not exist)
        if artwork is None:
            try:
                artwork_bytes = file.tags['APIC:'].data
                artwork_mimetype = file.tags['APIC:'].mime
            except KeyError:
                artwork_bytes = None
                artwork_mimetype = None
            artwork = Document(content=artwork_bytes,contentType=artwork_mimetype)

        # Convert tags to Album
        if album is None:
            album_name = file.tags['TALB'].text[0]
            release_year = file.tags['TDRC'][0].year
            album = Album(title=album_name,release_year=release_year,track_count=0)
    album = Album(album.title,release_year=album.release_year,track_count=len(tracks))

    # 1. If the album art exists, post it and get the ID. Otherwise, use ID 1 (default ava)
    artwork_reference = post_artwork(artwork)

    # 2. Insert the album, coverReference is the album art
    album_reference = post_album(album,artwork_reference)

    # 3. For each (recording/track), insert the recording, then the track.

    # If there are duplicate ordinals, wipe them and assign in ascending order
    dupes = [t.ordinal for t in tracks]
    if len(set(dupes)) != len(dupes):
        print('assignign new ordinals...')
        for (i,t) in enumerate(tracks,1):
            t.ordinal = i
    for (recording,track) in zip(recordings,tracks):
        a = recording_reference = post_recording(recording)
        b = post_track(track,recording_reference=recording_reference,album_reference=album_reference)

"""
clear();
(async function() {
  res = await fetch('http://localhost:8001/services/documents/343')
  buffer = await res.blob()
  url = window.URL.createObjectURL(buffer)
  audio = new Audio()
  document.querySelector('main audio').src = url
})()"""

