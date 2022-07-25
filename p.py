from flask import Flask, render_template, request, session, redirect, url_for, flash
from multiprocessing import connection
import pymysql

connection = pymysql.connect(host="localhost" , user="root", password="Hulkiscool", database="streamify")
cur = connection.cursor()

app = Flask(__name__)
app.secret_key  = 'mahinthejackfruit'

''''''''''''''''
@app.route('/')
def index():
    return render_template('login.html')

    print("Connected to database")

cur.execute("SELECT * FROM liked_songs")
print("Executed query")
result = cur.fetchall()
print(result)
'''''''''''''''

#index page that determines whether to go home for artist/listener or go home
@app.route('/', methods=['GET', 'POST'])#i changed this!
def home():
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
     # Check if user is loggedin
    if 'loggedin' in session:
        cur.execute('SELECT * FROM listener WHERE email = %s', [session['id']])
        account = cur.fetchone()

        if account:
            return render_template('home.html', results = results)
        else:
            return render_template('homepageartist.html', results = results)
        # User is loggedin show them the home page
        #return render_template('homepageauthor.html')
    # User is not loggedin redirect to login page
    print('new session')
    return redirect(url_for('login'))

#route for logging in to streamify
@app.route('/login', methods=['GET', 'POST'])#i changed this!
def login():
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
    print('in login page')
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        print(username, password)
        # Check if account exists using MySQL
        cur.execute('SELECT email, password FROM artist WHERE email= %s AND password = %s UNION SELECT email, password FROM listener WHERE email= %s AND password = %s', (username, password, username, password))
        # Fetch one record and return result
        account = cur.fetchone()

        print(account)
   
    # If account exists in accounts table in out database
        if account:
# Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = username
            print(session['id'])
            # Redirect to home page
            #return 'Logged in successfully!'
            print('it worked')
            cur.execute('SELECT * FROM artist WHERE email = %s', [username])
            account = cur.fetchone()

            if account:
                return render_template('homepageartist.html', results = results) #supposed to be song.html testing other html with this 
            else:
                return render_template('home.html', results =results)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            print('unsuccessful')
    
    return render_template('login.html', msg=msg) 

#route for registering to streamify    
@app.route('/register', methods=['GET', 'POST'])
def register():
    artist_id = cur.execute("SELECT COUNT(*) FROM artist")
    artist_id = cur.fetchone()[0]
    artist_id += 1
    if request.method == 'POST':
        print('here')
        name = request.form['name']
        print(name)
        email = request.form['email']
        print(email)
        phone = request.form['phone']
        print(phone)
        usertype = request.form['usertype']
        print(usertype)
        password = request.form['password']
        print(password)
        confpass = request.form['confirmpass']
        print(confpass)

        if password != confpass:
            msg = 'Passwords do not match'
            return render_template('register.html', msg=msg)

        if usertype == 'artist':
            cur.execute('INSERT INTO artist ( artist_id, name, password, phone_num, email) VALUES (%s, %s, %s, %s, %s)', (artist_id, name, password, phone, email ))
            connection.commit()

        else:
            user_id = cur.execute("SELECT COUNT(*) FROM listener")
            user_id = cur.fetchone()[0]
            user_id += 1
            cur.execute('INSERT INTO listener ( user_id, name, password, phone_num, email) VALUES (%s, %s, %s, %s, %s)', ( user_id, name, password, phone, email ))
            connection.commit()


        msg = 'Account successfully created!'
        return render_template('login.html', msg=msg)

    return render_template('register.html')
    

#route for retrieving lost/forgotten password
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    msg = ''
    if request.method == "POST":
        email = request.form['email']
        print(email)
        phone_num= request.form['phone_num']
        print(phone_num)

        cur.execute('SELECT password FROM artist WHERE email = %s and phone_num = %s UNION SELECT password FROM listener WHERE email = %s and phone_num = %s', (email, phone_num, email, phone_num))
        valid = cur.fetchone()


        if valid:
            print('Valid')
            password = valid[0]
            print(password)
            msg = 'Your password is ' + password
            flash(msg)
            return render_template('retrievepass.html', msg = msg)

    return render_template('retrievepass.html')

#route for users to manage their streamify account
#revise
@app.route('/manageart', methods=['GET', 'POST'])
def manageart():
    msg = ''

    if request.method == 'POST':
        cur.execute("SELECT artist_id FROM artist WHERE email = %s", [session['id']])
        artist_id = cur.fetchone()
        print(cur._last_executed)
        print(session['id'])
        print(artist_id)
        to_update = request.form['to_update']
        print(to_update)
        new_val = request.form['newval']
        print(new_val)
        password = request.form['password']
        print(password)

        cur.execute('SELECT * FROM artist WHERE password = %s', [password])
        valid = cur.fetchall()
        print(valid)

        if valid:
            print('valid artist')
            statement1 = 'Update artist SET %s = ' 
            statement2 = '%s WHERE artist_id = %s'
            value = to_update
            inputs = (new_val, artist_id[0])
            new = statement1 % value
            print(new)
            input = new + statement2
            print(input)
            cur.execute(input, inputs)
            connection.commit()
            print(cur._last_executed)
            print(cur.execute('Select name from artist where artist_id = %s', [artist_id] ))
            msg = 'Account change successful!'
            return render_template('manage.html', msg = msg)
        
        else:
            msg = 'Incorrect Password'
            return render_template('manage.html', msg = msg)

    return render_template('manage.html')

#might not be neccessary
@app.route('/managelist', methods=['GET', 'POST'])
def managelist():
    msg = ''

    if request.method == 'POST':
        cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
        listener_id = cur.fetchone()
        print(cur._last_executed)
        print(session['id'])
        print(listener_id)
        to_update = request.form['to_update']
        print(to_update)
        new_val = request.form['newval']
        print(new_val)
        password = request.form['password']
        print(password)

        valid = cur.execute('SELECT * FROM listener WHERE password = %s', [password])

        if valid:
            print('valid')
            statement1 = 'Update listener SET %s = ' 
            statement2 = '%s WHERE user_id = %s'
            value = to_update
            inputs = (new_val, listener_id[0])
            new = statement1 % value
            print(new)
            input = new + statement2
            print(input)
            cur.execute(input, inputs)
            connection.commit()
            print(cur._last_executed)
            print(cur.execute('Select name from listener where user_id = %s', [listener_id] ))
            msg = 'Account change successful!'
            return render_template('managelist.html', msg = msg)
        else:
            msg = "Incorrect Password"
            return render_template('managelist.html', msg = msg)

    return render_template('managelist.html')

#route for listeners to look up music on streamify
@app.route('/search', methods=['GET', 'POST'])
def search():
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    id = cur.fetchone()
    msg = ''
    if request.method == "POST":
        cur.execute('SELECT playlist_name, playlist_id FROM playlist WHERE user_id = %s', [id[0]])
        playlists = cur.fetchall()
        for playlist in playlists:
            print(playlist[0])
        search = request.form['searchval']
        print(search)
        input = '%' + search + '%'
        print(input)
        cur.execute("SELECT title, genre, release_date, name, song_id FROM song natural join artist WHERE title LIKE %s", input)
        print(cur._last_executed)
        results = cur.fetchall()
        if results:
            print(results)
            msg = 'Results:'
            return render_template("search.html", msg = msg, playlists = playlists, results = results)
        else:
            msg = 'Sorry we could not find anything'
            return render_template('search.html', msg = msg)
    
    return render_template('search.html')

#route that takes users to their streamify library
@app.route('/library', methods=['GET', 'POST'])
def library():
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    id = cur.fetchone()
    print(id)
    cur.execute("SELECT song_id, title, name FROM liked_songs natural join song natural join artist WHERE user_id = %s", (id[0]))
    print(cur._last_executed)
    library = cur.fetchall()
    msg = ''
    if request.method == "POST":
        search = request.form['searchval']
        print(search)
        input = '%' + search + '%'
        print(input)
        #cur.execute("SELECT title, genre, release_date, name, song_id FROM song natural join artist WHERE title LIKE %s", input)
        cur.execute("SELECT song_id, title, name FROM liked_songs natural join song natural join artist WHERE title LIKE %s and user_id = %s", (input, id[0]))
        print(cur._last_executed)
        library = cur.fetchall()
        if library:
            print(library)
            msg = 'Results:'
            return render_template("library.html", msg = msg, library = library)
        else:
            msg = 'Sorry we could not find anything'
        return render_template('library.html', msg = msg)
    return render_template('library.html', library = library)

#route for users to logout of streamify
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   # Redirect to login page
   return redirect(url_for('home'))

#route for users to like songs and add to library on streamify
@app.route('/like/<songid>', methods=['GET'])
def like(songid):
    print(songid)
    print("in like function")
    msg = ''
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    user_id = cur.fetchone()
    print(user_id)
    print(cur._last_executed)
    statement = 'INSERT INTO liked_songs (song_id, user_id) VALUES(%s, '
    statement2 = '%s)' % user_id[0]
    finalstatement = statement + statement2
    print(finalstatement)
    try:
        cur.execute(finalstatement, songid)
        connection.commit()
        #cur.execute("INSERT INTO liked_songs (song_id, user_id) VALUES(%d, %d)", (songid, user_id[0]))
        print(cur._last_executed)
        msg = 'Song added to liked songs'
    except:
        msg = 'Song already liked'
        return render_template('search.html', msg = msg)
    else:
        return render_template('search.html', msg = msg)

#route for users to add songs to playlists
@app.route('/addtoplaylist/<songid>/<playlistid>', methods=['GET'])
def addtoplaylist(songid, playlistid):
    print(songid)
    print(playlistid)
    print("in add to playlist function")
    msg = ''
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    user_id = cur.fetchone()
    print(user_id)
    print(cur._last_executed)
    #values = (songid, user_id[0])
    #statement = 'INSERT INTO liked_songs VALUES(song_id, user_id) VALUES(%d, %d)' % values
    #print(statement)
    #cur.execute(statement, args=None)
    try:
        cur.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES(%s, %s)", (playlistid, songid))
        print(cur._last_executed)
        connection.commit()
        msg = 'Song added to playlist'
    
    except:
        msg = 'Song Already in this playlist'
        return render_template('search.html', msg = msg)
    else:
        return render_template('search.html', msg = msg)

#route for users to view/manage their playlists
@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    id = cur.fetchone()
    print(id)
    msg = ''
    cur.execute('SELECT playlist_name, playlist_id FROM playlist WHERE user_id = %s', [id[0]])
    playlists = cur.fetchall()
    print(playlists)
    for playlist in playlists:
        print(playlist[0])

    if request.method == "POST":
        print('in post')
        playlist_id = cur.execute("SELECT COUNT(*) FROM playlist")
        print(cur._last_executed)
        playlist_id = cur.fetchone()[0]
        playlist_id += 1
        new_playlist = request.form['newplaylist']
        cur.execute("INSERT INTO playlist (playlist_id, playlist_name, user_id) VALUES(%s, %s, %s)", (playlist_id, new_playlist, id[0]))
        print(cur._last_executed)
        connection.commit
        msg = 'Playlist Created'
        return render_template("home.html", msg = msg, results=results)

    return render_template("playlist.html", playlists = playlists)

#route for users to delete their streamify playlists
@app.route('/deleteplaylist/<playlistid>')
def deleteplaylist(playlistid):
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
    print('in delete playlist function')
    cur.execute('DELETE FROM playlist WHERE playlist_id = %s', [playlistid])
    #connection.commit()
    print(cur._last_executed)
    msg = 'Playlist Deleted'
    return render_template("home.html", msg = msg, results = results)

#route for users to see the songs in their playlists
@app.route('/playlist_songs/<playlist_id>', methods=['GET', 'POST'])
def playlist_songs(playlist_id):
    cur.execute("SELECT playlist_name, playlist_id FROM playlist WHERE playlist_id = %s", (playlist_id))
    playlist_name = cur.fetchone()
    print(playlist_name)
    cur.execute("SELECT song_id, title, name FROM playlist_songs NATURAL JOIN song NATURAL JOIN artist WHERE playlist_id = %s", (playlist_id))
    print(cur._last_executed)
    library = cur.fetchall()
    print(library)
    msg = ''
    if request.method == "POST":
        search = request.form['searchval']
        print(search)
        input = '%' + search + '%'
        print(input)
        #cur.execute("SELECT title, genre, release_date, name, song_id FROM song natural join artist WHERE title LIKE %s", input)
        cur.execute("SELECT song_id, title, name FROM playlist_songs natural join song natural join artist WHERE title LIKE %s and playlist_id = %s", (input, playlist_id))
        print(cur._last_executed)
        library = cur.fetchall()
        if library:
            print(library)
            msg = 'Results:'
            return render_template("playlistsongs.html", msg = msg, library = library)
        else:
            msg = 'Sorry we could not find anything'
            return render_template('playlistsongs.html', msg = msg)
    print('made it to the end')
    return render_template('playlistsongs.html', library = library, playlist_name = playlist_name)

#route for artists to see the statistics of their songs
@app.route('/statistics')
def statistics():
    cur.execute("SELECT artist_id FROM artist WHERE email = %s", [session['id']])
    print(cur._last_executed)
    id = cur.fetchone()
    print(id)
    msg = ''
    cur.execute('SELECT likes, release_date, title FROM song WHERE artist_id = %s ORDER BY likes DESC;', [id[0]])
    top_songs = cur.fetchall()
    for songs in top_songs:
        print(songs[0])

    return render_template("statistics.html", top_songs = top_songs)

#route that allows artist to see their songs and manage them in a crud table
@app.route('/managesongs')
def managesongs():
    cur.execute("SELECT artist_id FROM artist WHERE email = %s", [session['id']])
    print(cur._last_executed)
    id = cur.fetchone()
    msg = ''
    cur.execute('SELECT title, release_date, genre, song_id FROM song WHERE artist_id = %s', [id[0]])
    songs = cur.fetchall()
    for song in songs:
        print(songs[0])

    return render_template("managesongs.html", songs = songs)

#route for artists to upload their songs
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
     # Check if user 
    if request.method == "POST":
        #algorithm for getting new song id
        song_id = cur.execute("SELECT COUNT(*) FROM song")
        song_id = cur.fetchone()[0]
        song_id += 1

        release_date = 0

        #algorithm for getting the artist id
        cur.execute("SELECT artist_id FROM artist WHERE email = %s", [session['id']])
        print(cur._last_executed)
        id = cur.fetchone()
        print(id)

        song_name = request.form['title']
        genre = request.form['genre']
        cur.execute('INSERT INTO song (song_id, likes, genre, title, artist_id) VALUES(%s, 0, %s, %s, %s)', (song_id, genre, song_name, id[0]))
        print(cur._last_executed)
        connection.commit()
        msg = 'Song Uploaded'

        return render_template('homepageartist.html', msg = msg, results=results)

    return render_template('uploadmusic.html')

#removes songs from library
@app.route('/remove_song/<song_id>')
def remove_song(song_id):
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
     # Check if user 
    cur.execute("SELECT user_id FROM listener WHERE email = %s", [session['id']])
    id = cur.fetchone()
    print(id)

    cur.execute('DELETE FROM liked_songs WHERE song_id = %s and user_id = %s', (song_id, id))#query for removing song from liked_songs
    connection.commit
    msg = 'Song removed from library'

    return render_template('home.html', msg = msg, results=results)

#removes songs from a playlist
@app.route('/remove_song_playlist/<song_id>/<playlist_id>')
def remove_song_playlist(song_id, playlist_id):
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
     # Check if user 
    cur.execute('DELETE FROM playlist_songs WHERE song_id = %s AND playlist_id = %s', (song_id, playlist_id))
    connection.commit
    print(cur._last_executed)
    msg = 'Song removed from playlist'
    
    return render_template('home.html', msg = msg, results = results)

#deletes a playlist
@app.route('/delete_playlist/<playlist_id>')
def delete_playlist(playlist_id):
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
    cur.execute('DELETE FROM playlist WHERE playlist_id = %s', playlist_id)
    print(cur._last_executed)
    connection.commit()
    msg = 'Playlist deleted'
    return render_template('home.html', msg = msg, results=results)

#deletes songs off streamify
@app.route('/delete_song/<song_id>')
def delete_song(song_id):
    cur.execute('SELECT * FROM song ORDER BY likes DESC LIMIT 5')
    results = cur.fetchall()
    for song in results:
        print(song)
     # Check if user 
    cur.execute('DELETE FROM song WHERE song_id = %s', [song_id])
    cur.execute('DELETE FROM liked_songs WHERE song_id = %s', (song_id))#query for removing song from liked_songs
    cur.execute('DELETE FROM playlist_songs WHERE song_id = %s', (song_id))#query for removing song from liked_songs
    print(cur._last_executed)
    connection.commit()
    msg = 'Song deleted from Streamify'
    return render_template('homepageartist.html', msg = msg, results=results)

