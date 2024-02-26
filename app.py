from bottle import request, static_file, route, run, template, redirect
import socket
import sqlite3
from tinytag import TinyTag
from cli_color_py import magenta, blink, yellow, blue, red, bright_yellow, green, bold
import os


host=socket.gethostname()
ip = socket.gethostbyname(host)

print(blink(magenta("HIPI By Frostie Studios")))
print(green("Server Starting"))
print(green("ServerInfo"))
print(bold(blue("HOST:")))
print(blue(f"http://{(host)}:8080/"))

print(bold(blue("IP:")))
print(blue(ip))
username = "matt"

#Current Server
current_server = "LOCAL"
print()
#directories

CURR_DIR = ''
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

@route('/media/music/<artist>/<album/<filename:path>')
def play(filename):
    return static_file(filename,root='./media/music/')

@route('/media/play/<artist>/<album>/<file_name:path>')
def play_audio(artist, album, file_name):
    return '''
    <audio controls autoplay>
        <source src="/media/music/{}/{}/{}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    '''.format(artist, album, file_name)
@route('/media/music/<filepath:path>')
def serve_music(filepath):
    return static_file(filepath, root=MUSIC_DIR)
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
            fname = uploaded_file.filename
            print(fname)
            tag = TinyTag.get(tmp_file)
            title = tag.title
            artist = tag.artist
            album = tag.album
            track = tag.track
            print(yellow(bold(title)))
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
                    c.execute("INSERT INTO music (title, artist, album, track, file) VALUES (?, ?, ?, ?, ?)", (title, artist, album, track, fname))
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
# Route to handle playing audio file
# Route to handle playing audio file and processing form submission
@route('/media')
def media():
    print(bright_yellow("MEDIA"))
    c.execute("SELECT id, title, artist, album, track, file FROM music")
    result = c.fetchall()
    conn.commit()
    output = template('pages/media.html', rows=result)
    return output

@route('/settings')
def settings():
    print("Settings")
    return("Settings")
@route('/settings/newlocation')
def new():
    print(yellow("NEW LOCATION"))
@route('/recorder')
def recorder():
    print(bright_yellow("REC"))
    return("Record")
run(debug=True,reloader=True,host="localhost", port=8080)
