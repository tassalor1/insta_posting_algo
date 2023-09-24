import sqlite3

conn = sqlite3.connect('insta_hashtag.db')
cur = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS insta_hashtag (
    id TEXT PRIMARY KEY,
    type TEXT,
    shortCode TEXT,
    caption TEXT,
    hashtags TEXT,
    mentions TEXT,
    url TEXT,
    commentsCount INTEGER,
    dimensionsHeight INTEGER,
    dimensionsWidth INTEGER,
    displayUrl TEXT,
    images TEXT,
    alt TEXT,
    likesCount INTEGER,
    timestamp TEXT,
    ownerId TEXT
);
"""

cur.execute(create_table_query)
conn.commit()
conn.close()

print("Database and table created successfully!")
