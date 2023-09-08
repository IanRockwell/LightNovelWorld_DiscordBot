import sqlite3
import os

# Define the path to the data folder
data_folder = 'data'  # Change this to the desired folder name

# Create the data folder if it doesn't exist
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Specify the database file path inside the data folder
db_file_path = os.path.join(data_folder, 'novel_database.db')


# Function to connect to the SQLite database and ensure tables exist
def connect_and_create_tables():
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Create a table to store novels if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            novelid TEXT PRIMARY KEY,
            latest_chapter TEXT,
            url TEXT
        )
    ''')

    # Create a table to store subscribers if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            novelid TEXT,
            userid TEXT,
            FOREIGN KEY (novelid) REFERENCES novels (novelid)
        )
    ''')

    return conn, cursor


# Function to add a new novel
def add_novel(novelid, latest_chapter, url):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT COUNT(*) FROM novels WHERE novelid = ?', (novelid,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Novel with this novelid doesn't exist, insert a new row
        cursor.execute('''
            INSERT INTO novels (novelid, latest_chapter, url)
            VALUES (?, ?, ?)
        ''', (novelid, latest_chapter, url))
    else:
        # Novel with this novelid already exists, update it
        cursor.execute('''
            UPDATE novels
            SET latest_chapter = ?, url = ?
            WHERE novelid = ?
        ''', (latest_chapter, url, novelid))

    conn.commit()
    conn.close()


# Function to get the URL of a novel
def get_novel_url(novelid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT url FROM novels WHERE novelid = ?', (novelid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# Function to get the latest chapter of a novel
def get_novel_latest_chapter(novelid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT latest_chapter FROM novels WHERE novelid = ?', (novelid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# Function to get a list of subscribers to a novel
def get_novel_subscribers(novelid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT userid FROM subscribers WHERE novelid = ?', (novelid,))
    subscribers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subscribers


# Function to get a list of novels a user is subscribed to
def get_user_subscriptions(userid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT novelid FROM subscribers WHERE userid = ?', (userid,))
    subscriptions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subscriptions


# Function to add a new subscriber to a novel
def add_novel_subscriber(novelid, userid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('INSERT INTO subscribers (novelid, userid) VALUES (?, ?)', (novelid, userid))
    conn.commit()
    conn.close()


# Function to list all novels with at least one subscriber
def get_novels_with_subscribers():
    conn, cursor = connect_and_create_tables()
    cursor.execute('''
        SELECT DISTINCT novels.novelid, novels.latest_chapter, novels.url
        FROM novels
        INNER JOIN subscribers ON novels.novelid = subscribers.novelid
    ''')
    novels_with_subscribers = cursor.fetchall()
    conn.close()
    return novels_with_subscribers


# Function to remove a subscriber from a novel
def remove_novel_subscriber(novelid, userid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('DELETE FROM subscribers WHERE novelid = ? AND userid = ?', (novelid, userid))
    conn.commit()
    conn.close()


# Function to unsubscribe a user from all novels they're subscribed to
def unsubscribe_user_from_all_novels(userid):
    conn, cursor = connect_and_create_tables()
    cursor.execute('DELETE FROM subscribers WHERE userid = ?', (userid,))
    conn.commit()
    conn.close()


# Function to modify a novel's latest chapter number
def modify_novel_latest_chapter(novelid, new_latest_chapter):
    conn, cursor = connect_and_create_tables()
    cursor.execute('SELECT COUNT(*) FROM novels WHERE novelid = ?', (novelid,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Novel with this novelid doesn't exist, you can choose to handle this case accordingly
        conn.close()
        return False
    else:
        # Novel with this novelid exists, update its latest chapter
        cursor.execute('''
            UPDATE novels
            SET latest_chapter = ?
            WHERE novelid = ?
        ''', (new_latest_chapter, novelid))

        conn.commit()
        conn.close()
        return True
