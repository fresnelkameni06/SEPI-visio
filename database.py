import pandas as pd
import sqlite3
import hashlib


DB_NAME = "visio_database.db"


def compute_uploaded_file_hash(uploaded_file):
    uploaded_file.seek(0)
    sha256 = hashlib.sha256()
    sha256.update(uploaded_file.getvalue())
    return sha256.hexdigest()


def compute_image_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def image_hash_exists(image_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM images WHERE image_hash=? LIMIT 1", (image_hash,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def get_filepath_from_hash(image_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM images WHERE image_hash = ? LIMIT 1", (image_hash,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_data_from_hash(image_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE image_hash = ? LIMIT 1", (image_hash,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None


def get_db_as_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM images", conn)
    conn.close()
    return df


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS images (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            image_hash TEXT UNIQUE,
                                                            filename TEXT,
                                                            initial_filename TEXT,
                                                            filepath TEXT,
                                                            upload_date TEXT,
                                                            manual_annotation TEXT,
                                                            ai_annotation TEXT,
                                                            ai_confidence REAL,
                                                            ai_score INTEGER,
                                                            file_size INTEGER,
                                                            width INTEGER,
                                                            height INTEGER,
                                                            aspect_ratio REAL,
                                                            avg_r REAL,
                                                            avg_g REAL,
                                                            avg_b REAL,
                                                            min_r INTEGER,
                                                            min_g INTEGER,
                                                            min_b INTEGER,
                                                            max_r INTEGER,
                                                            max_g INTEGER,
                                                            max_b INTEGER,
                                                            avg_l INTEGER,
                                                            brightness REAL,
                                                            contrast REAL,
                                                            saturation REAL,
                                                            colorfulness REAL,
                                                            dark_ratio REAL,
                                                            edge_density REAL,
                                                            texture REAL,
                                                            entropy REAL,
                                                            green_ratio REAL,
                                                            sharpness REAL,
                                                            max_zone_edges REAL,
                                                            zone_variance REAL,
                                                            bottom_edge_density REAL,
                                                            ground_clutter REAL,
                                                            green_zone_max REAL,
                                                            green_zone_var REAL,
                                                            histogram_r TEXT,
                                                            histogram_g TEXT,
                                                            histogram_b TEXT,
                                                            histogram_l TEXT,
                                                            hue_histogram TEXT,
                                                            bin_histogram_r TEXT,
                                                            bin_histogram_g TEXT,
                                                            bin_histogram_b TEXT,
                                                            bin_hue_histogram TEXT)""")
    conn.commit()
    conn.close()


def insert_image(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO images(
        initial_filename, filename, image_hash, filepath, upload_date,
        manual_annotation, ai_annotation, ai_confidence, ai_score,
        file_size, width, height, aspect_ratio,
        avg_r, avg_g, avg_b, min_r, min_g, min_b, max_r, max_g, max_b, avg_l,
        brightness, contrast, saturation, colorfulness,
        dark_ratio, edge_density, texture, entropy, green_ratio, sharpness,
        max_zone_edges, zone_variance, bottom_edge_density, ground_clutter,
        green_zone_max, green_zone_var,
        histogram_r, histogram_g, histogram_b, histogram_l, hue_histogram,
        bin_histogram_r, bin_histogram_g, bin_histogram_b, bin_hue_histogram)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", data)
    conn.commit()
    conn.close()


def update_manual_annotation(m_annotation, image_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE images SET manual_annotation=? WHERE image_hash=?", (m_annotation, image_hash))
    conn.commit()
    conn.close()


"""
def update_ai_annotation(ai_annotation, ai_confidence, ai_score, image_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE images SET ai_annotation=?, ai_confidence=?, ai_score=? WHERE image_hash=?",
        (ai_annotation, ai_confidence, ai_score, image_hash))
    conn.commit()
    conn.close()
"""
