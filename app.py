from bottle import request, static_file, route, run, template, redirect
from pytube import YouTube
import socket
import sqlite3
import music_tag
from tinytag import TinyTag
import os
host=socket.gethostname()
ip = socket.gethostbyname(host)
username = "matt"
#directories
MUSIC_DIR = 'media/music'
VIDEO_DIR = 'media/video'
TMP_DIR = 'media/tmp'
#make dir
for directory in (MUSIC_DIR, VIDEO_DIR, TMP_DIR):
    if not os.path.exists(directory):
        os.makedirs(directory)
#connect to database
media_db = "./hipi.db"
conn = sqlite3.connect(media_db)
c = conn.cursor()

@route('/pages/<filename:path>')
def serve_static(filename):
    return static_file(filename,root='./pages/')

@route('/')
def index():
    global username
    global host
    global ip
    return template('./pages/index.html',
                    username=username,
                    host=host,
                    ip=ip,
                    )
@route('/media/new')
def new():
    return template("pages/new_file")
@route('/media/new',method="POST")
def do_upload():
    uploaded_file = request.files.get('uploaded_file')
    if uploaded_file:
        media_type = uploaded_file.content_type.split('/')[0]
        #Audio
        if media_type == 'audio':
            tmp_file = os.path.join('tmp',uploaded_file.filename)
            uploaded_file.save(tmp_file)
            #Metadata Extract
            tag = TinyTag.get(tmp_file)
            title = tag.title
            artist = tag.artist
            album = tag.album
            track = tag.track
            print(title)
            print(artist)
            print(album)
            
            #delte tmp
            os.remove(tmp_file)
            #Sort
            if artist and album:
                #Add To Database
                c.execute("SELECT * FROM music WHERE title=? AND artist=? AND album=?", (title, artist, album))
                existing_entry = c.fetchone()

                if not existing_entry:
                    # Insert entry into the database
                    c.execute("INSERT INTO music (title, artist, album, track) VALUES (?, ?, ?, ?)", (title, artist, album, track))
                    conn.commit()
                #Sort Artist
                artist_dir = os.path.join(MUSIC_DIR, artist)
                if not os.path.exists(artist_dir):
                    os.makedirs(artist_dir)
                #Sort Album
                album_dir = os.path.join(artist_dir, album)
                if not os.path.exists(album_dir):
                    os.makedirs(album_dir)
                #Save
                filepath = os.path.join(album_dir, uploaded_file.filename)
                uploaded_file.save(filepath, overwrite=True)
                
                redirect('/media')
            else:
                return "WOMP WOMP"

        #Video
        elif media_type == 'video':
            filepath = os.path.join(VIDEO_DIR, uploaded_file.filename)
            uploaded_file.save(filepath)
            upload_dir = VIDEO_DIR
        redirect('/media')
    else:
        return "Unsuported Media"
@route('/media')
def media():
    c.execute("SELECT id, title, artist, album, track FROM music")
    result = c.fetchall()
    conn.commit()
    output = template('pages/media.html', rows=result)
    return output
@route('/download')
def Download():
    global yt_link
    youtubeObject = YouTube(yt_link)
    youtubeObject = youtubeObject.streams.get_audio_only(subtype='aac')
    try:
        youtubeObject.download()
    except:
        return ("Error")
    print("Download Finished")
    print(youtubeObject.title)

@route('/recorder')
def recorder():
    return("Record")
run(debug=True,reloader=True,host="localhost", port=8080)
