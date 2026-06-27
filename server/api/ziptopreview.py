import sqlite3

def create_previews_from_db(music_db, video_db, files_db, photo_db):
    #AUGHHHH WHY DO I HAVE TO MAiNTAIN 4 CONNECTIONS AY ONCE!!!
    music_connection = sqlite3.connect(music_db)
    video_connection = sqlite3.connect(video_db)
    file_connection = sqlite3.connect(files_db)
    photo_connection = sqlite3.connect(photo_db)
    previews_connection = sqlite3.connect("previews.db")

    music_cursor = music_connection.cursor()
    video_cursor = video_connection.cursor()
    file_cursor = file_connection.cursor()
    photo_cursor = photo_connection.cursor()
    preview_cursor = previews_connection()

    #TODO: Send a command to pull all the content and move it into a preview database.
    
    music_cursor.execute("SELECT * FROM *")
    musicrows = cursor.fetchall()
    for row in musicrows:
        #TODO: add logic to compress these together