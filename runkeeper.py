#!/usr/bin/env python3

import csv
import datetime
import sqlite3
import os
import shutil

# ------------------------------------------------------------
# Runkeeper -> GadgetBridge Activity Importer
# Folder layout:
#   runkeeper/  (csv + gpx)
#   database/   (Gadgetbridge db)
# ------------------------------------------------------------
# MAKE A BACKUP OF YOUR DATABASE FIRST
# ------------------------------------------------------------

database = "database/Gadgetbridge"
csv_file = "runkeeper/cardioActivities.csv"
gpx_source_dir = "runkeeper"
gpx_target_dir = "files"

device_id = 4
user_id = 1

GB_GPX_BASE = "/storage/emulated/0/Android/data/nodomain.freeyourgadget.gadgetbridge/files/"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def parse_datetime(dt_string):
    return datetime.datetime.strptime(dt_string.strip(), "%Y-%m-%d %H:%M:%S")


def parse_duration(duration_string):
    duration_string = duration_string.strip()
    parts = duration_string.split(":")

    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)

    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)

    return int(float(duration_string))


def iso_filename(dt, sport):
    local_dt = dt.astimezone()
    tz = local_dt.strftime("%z")
    tz = tz[:3] + "_" + tz[3:]
    timestamp = local_dt.strftime("%Y-%m-%dT%H_%M_%S")
    sport = sport.lower().replace(" ", "-")
    return f"gadgetbridge-{sport}-{timestamp}{tz}.gpx"


def map_sport(sport):
    s = sport.lower()
    if "run" in s:
        return 16
    if "walk" in s:
        return 32
    if "cycle" in s or "bike" in s:
        return 67109043
    if "hike" in s:
        return 4194304
    if "skat" in s:
        return 67108999
    return 0


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

conn = sqlite3.connect(database)
cursor = conn.cursor()

with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        # ---- Time ----
        start_dt = parse_datetime(row["Date"])
        duration_seconds = parse_duration(row["Duration"])
        end_dt = start_dt + datetime.timedelta(seconds=duration_seconds)

        start_ts = int(start_dt.timestamp())*1000
        end_ts = int(end_dt.timestamp())*1000

        # ---- Activity ----
        sport = row["Type"]
        sport_code = map_sport(sport)

        # ---- Name ----
        name = row["Route Name"].strip()
        if not name:
            name = sport

        # ---- Duplicate Check ----
        existing = cursor.execute(
            "SELECT _id FROM BASE_ACTIVITY_SUMMARY WHERE START_TIME=?",
            (start_ts,)
        ).fetchone()

        if existing:
            print("Skipping existing activity:", start_dt)
            continue

        # ---- GPX ----
        gpx_track_path = None
        source_gpx_name = row["GPX File"].strip()

        if source_gpx_name:
            source_gpx_path = os.path.join(gpx_source_dir, source_gpx_name)

            if os.path.exists(source_gpx_path):

                os.makedirs(gpx_target_dir, exist_ok=True)

                new_filename = iso_filename(start_dt, sport)
                target_path = os.path.join(gpx_target_dir, new_filename)

                shutil.copyfile(source_gpx_path, target_path)

                gpx_track_path = GB_GPX_BASE + new_filename

            else:
                print("WARNING: GPX not found:", source_gpx_path)

        # ---- Insert ----
        print("Inserting:", sport, start_dt)

        cursor.execute("""
            INSERT INTO BASE_ACTIVITY_SUMMARY
            (NAME, START_TIME, END_TIME, ACTIVITY_KIND,
             BASE_LONGITUDE, BASE_LATITUDE, BASE_ALTITUDE,
             GPX_TRACK, RAW_DETAILS_PATH,
             DEVICE_ID, USER_ID,
             SUMMARY_DATA, RAW_SUMMARY_DATA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            start_ts,
            end_ts,
            sport_code,
            None,
            None,
            None,
            gpx_track_path,
            None,
            device_id,
            user_id,
            None,
            None
        ))

conn.commit()
conn.close()

print("Import finished successfully.")