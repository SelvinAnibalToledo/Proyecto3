import os
import environ
import psycopg2
import sys
from pathlib import Path
import csv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)

env = environ.Env()
environ.Env.read_env('.env')
#print(env.str('DB_DSN'))
conn = psycopg2.connect(env.str('DB_DSN'))
cur = conn.cursor()

sql = 'SELECT * FROM collection_artist'
cur.execute(sql)
collection_exists = cur.fetchall()
print(collection_exists)



path =f'''{BASE_DIR}/wikiart/data/'''
print(path)
files = os.listdir(path)
artists = [f for f in files if '-art.csv' not in f]

for a in artists:
    with open(path+a, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            sql = """INSERT INTO collection_artist (slug, name, born_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (slug)
            DO NOTHING;"""
            cur.execute(sql, tuple(row))


artworks = [f for f in files if '-art.csv' in f]
# print(artworks)

for a in artworks:
    with open(path+a, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            # author_id
            # print(row)
            sql = "SELECT id FROM collection_artist WHERE slug = %s"
            cur.execute(sql, (row[0],))
            author_id = cur.fetchone()[0]

            # style
            style_id = None
            if row[4] != '':
                sql = """INSERT INTO collection_style (name)
                VALUES (%s)
                ON CONFLICT (name)
                DO NOTHING;"""
                cur.execute(sql, (row[4], ))
                sql = "SELECT id FROM collection_style WHERE name = %s"
                cur.execute(sql, (row[4],))
                style_id = cur.fetchone()[0]
                #print('estilo: ' + str(style_id) + 'estilo: ' + row[4])

            # period
            period_id = None
            if row[5] != '':
                sql = """INSERT INTO collection_period (name)
                VALUES (%s)
                ON CONFLICT (name)
                DO NOTHING;"""
                cur.execute(sql, (row[5], ))
                sql = "SELECT id FROM collection_period WHERE name = %s"
                cur.execute(sql, (row[5],))
                period_id = cur.fetchone()[0]
                #print('periodo: ' + str(period_id) + 'periodostr: ' + row[5])

            # genre
            genre_id = None
            if row[6] != '':
                print(row[6])
                sql = """INSERT INTO collection_genre (name)
                VALUES (%s)
                ON CONFLICT (name)
                DO NOTHING;"""
                cur.execute(sql, (row[6], ))
                sql = "SELECT id FROM collection_genre WHERE name = %s"
                cur.execute(sql, (row[6],))
                genre_id = cur.fetchone()[0]
                print("genre: "+ str(row[7]) + "genreid:" + str(genre_id))

            # artwork
            sql = """INSERT INTO collection_artwork (author_id, path, title,
                    date, style_id, period_id, genre_id, image_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (path)
            DO NOTHING;"""
            print(str(author_id) +' - ' + row[1] +' - ' +  row[2] +' - ' +  row[3] +' - ' +  str(style_id) +' - ' +  str(period_id) +' - ' +  str(genre_id) +' - ' +  row[7])
            cur.execute(sql, ((author_id), row[1], row[2], row[3], (style_id), (period_id), (genre_id), row[7] ))


conn.commit()