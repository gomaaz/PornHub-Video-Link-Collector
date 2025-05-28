#!/usr/bin/env python
import requests
import sys
import urllib.parse as urlparse
import sqlite3
import os
import re
from prettytable import PrettyTable
from sqlite3 import Error
from urllib import request
from bs4 import BeautifulSoup

# Database location
database = "./database.db"
# Output text file for URLs
URL_OUTPUT_FILE = "video_urls.txt"


# CHECKINGS
def type_check(item):
    if item == "model":
        print("Valid type (model) selected.")
    elif item == "pornstar":
        print("Valid type (pornstar) selected.")
    elif item == "channels":
        print("Valid type (channel) selected.")
    elif item == "users":
        print("Valid type (user) selected.")
    elif item == "playlist":
        print("Valid type (playlist) selected.")
    elif item == "all":
        print("Valid type (all) selected.")
    else:
        how_to_use("Not a valid type.")
        sys.exit()


def ph_url_check(url):
    parsed = urlparse.urlparse(url)
    regions = ["www", "cn", "cz", "de", "es", "fr", "it", "nl", "jp", "pt", "pl", "rt"]
    for region in regions:
        if parsed.netloc == region + ".pornhub.com":
            print("pornhub url validated.")
            return
    print("This is not a pornhub url.")
    sys.exit()


def ph_type_check(url):
    parsed = urlparse.urlparse(url)
    if parsed.path.split('/')[1] == "model":
        print("This is a MODEL url,")
    elif parsed.path.split('/')[1] == "pornstar":
        print("This is a PORNSTAR url,")
    elif parsed.path.split('/')[1] == "channels":
        print("This is a CHANNEL url,")
    elif parsed.path.split('/')[1] == "users":
        print("This is a USER url,")
    elif parsed.path.split('/')[1] == "playlist":
        print("This is a PLAYLIST url,")
    elif parsed.path.split('/')[1] == "view_video.php":
        print("This is a VIDEO url. Please paste a model/pornstar/user/channel/playlist url.")
        sys.exit()
    else:
        print("Somethings wrong with the url. Please check it out.")
        sys.exit()


def ph_alive_check(url):
    requested = requests.get(url)
    if requested.status_code == 200:
        print("and the URL is existing.")
    else:
        print("but the URL does not exist.")
        sys.exit()


def add_check(name_check):
    if name_check == "batch":
        u_input = input("Please enter full path to the batch-file.txt (or c to cancel): ")
        if u_input == "c":
            print("Operation canceled.")
        else:
            with open(u_input, 'r') as input_file:
                for line in input_file:
                    line = line.strip()
                    add_item(line)

    else:
        add_item(name_check)


def get_item_name(item_type, url_item):
    url = url_item
    html = request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, 'lxml')

    if item_type == "model":
        finder = soup.find(class_='nameSubscribe')
        title = finder.find(itemprop='name').text.replace('\n', '').strip()
    elif item_type == "pornstar":
        finder = soup.find(class_='nameSubscribe')
        title = finder.find(class_='name').text.replace('\n', '').strip()
    elif item_type == "channels":
        finder = soup.find(class_='bottomExtendedWrapper')
        title = finder.find(class_='title').text.replace('\n', '').strip()
    elif item_type == "users":
        finder = soup.find(class_='bottomInfoContainer')
        title = finder.find('a', class_='float-left').text.replace('\n', '').strip()
    elif item_type == "playlist":
        finder = soup.find(id='playlistTopHeader')
        title = finder.find(id='watchPlaylist').text.replace('\n', '').strip()
    else:
        print("No valid item type.")
        title = False

    return title


##################################### URL COLLECTION

def extract_video_urls(page_url):
    """Extract all video URLs from a given page (nur viewkey, keine pkey)."""
    try:
        html = request.urlopen(page_url).read().decode('utf8')
        soup = BeautifulSoup(html, 'lxml')
        video_urls = []
        # Find all video links, aber nur mit 'viewkey' und OHNE 'pkey'
        for link in soup.select('a[href*="/view_video.php"]'):
            video_path = link['href']
            # Prüfe: Muss 'viewkey' enthalten, aber nicht 'pkey'
            if 'viewkey' in video_path and 'pkey' not in video_path:
                if video_path.startswith('/'):
                    full_url = f"https://www.pornhub.com{video_path}"
                else:
                    full_url = video_path
                video_urls.append(full_url)
        return list(set(video_urls))  # Remove duplicates
    except Exception as e:
        print(f"Error extracting videos: {e}")
        return []


def extract_all_video_urls(base_url):
    """Iterate through all result pages to collect all video URLs from a listing."""
    all_video_urls = []
    page = 1
    # If base_url already contains a page number, start from that page and remove it from URL
    if 'page=' in base_url:
        parts = urlparse.urlsplit(base_url)
        qs = urlparse.parse_qs(parts.query)
        if 'page' in qs:
            try:
                page = int(qs['page'][0])
            except Exception:
                page = 1
            qs.pop('page', None)
        new_query = urlparse.urlencode(qs, doseq=True)
        base_url = urlparse.urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
        base_url = base_url.rstrip('?&')
    while True:
        page_url = f"{base_url}?page={page}" if '?' not in base_url else f"{base_url}&page={page}"
        video_urls = extract_video_urls(page_url)
        if not video_urls:
            break
        # Add new URLs (avoid duplicates across pages)
        for url in video_urls:
            if url not in all_video_urls:
                all_video_urls.append(url)
        page += 1
    return all_video_urls

def write_urls_to_file(urls):
    """Append multiple URLs to the output file"""
    try:
        with open(URL_OUTPUT_FILE, 'a') as f:
            for url in urls:
                f.write(url + '\n')
        print(f"Saved {len(urls)} URLs to file")
    except Exception as e:
        print(f"Error saving URLs: {e}")

def collect_all_items(conn):
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM ph_items")
    except Error as e:
        print(e)
        sys.exit()

    rows = c.fetchall()

    for row in rows:
        if row[1] == "model":
            url_after = "/videos/upload"
        elif row[1] == "users":
            url_after = "/videos/public"
        elif row[1] == "channels":
            url_after = "/videos"
        else:
            url_after = ""

        base_url = "https://www.pornhub.com/" + str(row[1]) + "/" + str(row[2]) + url_after
        print("-----------------------------")
        print(f"Collecting videos from: {base_url} (all pages)")
        video_urls = extract_all_video_urls(base_url)
        if video_urls:
            write_urls_to_file(video_urls)
        else:
            print("No videos found on page")
        print("-----------------------------")

def collect_all_new_items(conn):
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM ph_items WHERE new='1'")
    except Error as e:
        print(e)
        sys.exit()

    rows = c.fetchall()

    for row in rows:
        if str(row[1]) == "model":
            url_after = "/videos/upload"
        elif str(row[1]) == "users":
            url_after = "/videos/public"
        elif str(row[1]) == "channels":
            url_after = "/videos"
        else:
            url_after = ""

        base_url = "https://www.pornhub.com/" + str(row[1]) + "/" + str(row[2]) + url_after
        print("-----------------------------")
        print(f"Collecting new videos from: {base_url} (all pages)")
        video_urls = extract_all_video_urls(base_url)
        if video_urls:
            write_urls_to_file(video_urls)
        else:
            print("No videos found on page")
        print("-----------------------------")

def dl_start():
    conn = create_connection(database)
    with conn:
        print("Collecting new items URLs")
        collect_all_new_items(conn)
        print("Collecting all items URLs")
        collect_all_items(conn)

def custom_dl(name_check):
    if name_check == "batch":
        u_input = input("Please enter full path to the batch-file.txt (or c to cancel): ")
        if u_input == "c":
            print("Operation canceled.")
        else:
            with open(u_input, 'r') as input_file:
                for line in input_file:
                    line = line.strip()
                    custom_dl_download(line)
    else:
        custom_dl_download(name_check)

def custom_dl_download(url):
    ph_url_check(url)
    ph_alive_check(url)
    print(f"Extracting videos from: {url} (all pages)")
    video_urls = extract_all_video_urls(url)
    if video_urls:
        write_urls_to_file(video_urls)
    else:
        print("No videos found on page")

def add_item(name_check):
    parsed = urlparse.urlparse(name_check)
    ph_url_check(name_check)
    ph_type_check(name_check)
    ph_alive_check(name_check)
    item_type = parsed.path.split('/')[1]
    item_url_name = parsed.path.split('/')[2]
    item_name = get_item_name(item_type, name_check)

    conn = create_connection(database)
    c = conn.cursor()
    try:
        c.execute("SELECT count(*) FROM ph_items WHERE url_name = ?", (item_name,))
    except Error as e:
        print(e)
        sys.exit()

    data = c.fetchone()[0]
    if data == 0:
        with conn:
            item = (item_type, item_url_name, item_name, '1')
            create_item(conn, item)
        print(item_name + " added to database.")
    else:
        print("Item already exists in database")


##################################### DATABASE ORIENTED

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_item(conn, item):
    sql = ''' INSERT INTO ph_items(type,url_name,name,new)
              VALUES(?,?,?,?) '''
    c = conn.cursor()
    c.execute(sql, item)
    return c.lastrowid

def select_all_items(conn, item):
    c = conn.cursor()
    if item == "all":
        c.execute("SELECT * FROM ph_items")
    else:
        c.execute("SELECT * FROM ph_items WHERE type='" + item + "'")

    rows = c.fetchall()

    t = PrettyTable(['Id.', 'Name', 'Type', 'Date created', 'Last checked', 'Url'])
    t.align['Id.'] = "l"
    t.align['Name'] = "l"
    t.align['Type'] = "l"
    t.align['Date created'] = "l"
    t.align['Last checked'] = "l"
    t.align['Url'] = "l"
    for row in rows:
        url = "https://www.pornhub.com/" + str(row[1]) + "/" + str(row[2])
        t.add_row([row[0], row[3], row[1], row[5], row[6], url])
    print(t)

def list_items(item):
    conn = create_connection(database)
    with conn:
        print("Listing items from database:")
        select_all_items(conn, item)

def delete_single_item(conn, id):
    sql = 'DELETE FROM ph_items WHERE id=?'
    c = conn.cursor()
    c.execute(sql, (id,))
    conn.commit()

def delete_item(item_id):
    conn = create_connection(database)
    with conn:
        delete_single_item(conn, item_id)

def create_config(conn, item):
    sql = ''' INSERT INTO ph_settings(option, setting)
              VALUES(?,?) '''
    c = conn.cursor()
    c.execute(sql, item)
    return c.lastrowid

def prepare_config():
    conn = create_connection(database)
    u_input = input("Please enter the FULL PATH to your download location: ")
    with conn:
        item = ('DownloadLocation', u_input)
        item_id = create_config(conn, item)

def get_dl_location(option):
    conn = create_connection(database)
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT * FROM ph_settings WHERE option='" + option + "'")
        rows = c.fetchall()
        for row in rows:
            dllocation = row[2]
        return dllocation
    else:
        print("Error! somethings wrong with the query.")

def check_for_database():
    print("Running startup checks...")
    if os.path.exists(database):
        print("Database exists.")
    else:
        print("Database does not exist.")
        print("Looks like this is your first time run...")
        first_run()

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Tables created.")
    except Error as e:
        print(e)

def create_tables():
    sql_create_items_table = """ CREATE TABLE IF NOT EXISTS ph_items (
                                        id integer PRIMARY KEY,
                                        type text,
                                        url_name text,
                                        name text,
                                        new integer DEFAULT 1,
                                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP,
                                        lastchecked DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """

    sql_create_settings_table = """ CREATE TABLE IF NOT EXISTS ph_settings (
                                        id integer PRIMARY KEY,
                                        option text,
                                        setting text,
                                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create items table
        create_table(conn, sql_create_items_table)
        create_table(conn, sql_create_settings_table)
        prepare_config()
    else:
        print("Error! cannot create the database connection.")


##################################### Lets do it baby

def first_run():
    create_tables()
    # Initialize output file
    open(URL_OUTPUT_FILE, 'w').close()


##################################### MESSAGING

def how_to_use(error):
    print("Error: " + error)
    print("Please use the tool like this:")
    t = PrettyTable(['Tool', 'command', 'item'])
    t.align['Tool'] = "l"
    t.align['command'] = "l"
    t.align['item'] = "l"
    t.add_row(['phdler', 'start', ''])
    t.add_row(['phdler', 'custom', 'url (full pornhub url) | batch (for .txt file)'])
    t.add_row(['phdler', 'add', 'model | pornstar | channel | user | playlist | batch (for .txt file)'])
    t.add_row(['phdler', 'list', 'model | pornstar | channel | user | playlist | all'])
    t.add_row(['phdler', 'delete', 'model | pornstar | channel | user | playlist'])
    print(t)

def help_command():
    print("------------------------------------------------------------------")
    print("You asked for help, here it comes! Run phdler with these commands:")
    t = PrettyTable(['Command', 'argument', 'description'])
    t.align['Command'] = "l"
    t.align['argument'] = "l"
    t.align['description'] = "l"
    t.add_row(['start', '', 'collect all video URLs from database items'])
    t.add_row(['custom', 'url | batch', 'extract video URLs from a specific page'])
    t.add_row(
        ['add', 'model | pornstar | channel | user | playlist | batch (for .txt file)', 'adding item to database'])
    t.add_row(['list', 'model | pornstar | channel | user | playlist', 'list selected items from database'])
    t.add_row(['delete', 'model | pornstar | channel | user | playlist', 'delete selected items from database'])
    print(t)
    print(f"All collected video URLs are saved in: {URL_OUTPUT_FILE}")
    print("------------------------------------------------------------------")
