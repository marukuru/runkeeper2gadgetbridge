# Runkeeper 🏃 2 GadgetBridge ✊
## About
Imports activity data from a Runkeeper backup into [GadgetBridge](https://gadgetbridge.org/).
## Usage
0. Make sure to keep a copy of your original GadgetBridge backup. Use at your own risk
1. Request a full export at [Runkeeper](https://runkeeper.com/exportData) or "Account Settings" → "Export Data"
2. Export a full backup in GadgetBridge: "Data management" → "Export zip"
3. Unpack your `gadgetbridge_<timestamp>.zip` to a new folder
4. Create a folder called `runkeeper/` in that new folder
5. Unpack your runkeeper backup into the newly created `runkeeper/` folder
	1. The `runkeeper/` folder should now contain a bunch of `.gpx` files as well as a `cardioActivities.csv` file
6. Adjust `device_id = 4` and `user_id = 1` in `runkeeper.py` to match your GadgetBridge device and user
7. Run `runkeeper.py` in your gadgetbridge backup folder
8. Pack the `database/`, `files/`, and `preferences/` folders and the `gadgetbridge.json` into a ZIP file: `zip -r - "database" "files" "preferences" "gadgetbridge.json" > "gadgetbridge_modified.zip"`
9. Import into GadgetBridge: “Data management” → "Import zip”
	1. You might see an error after importing about being unable to import files from `files/`, just ignore and wait for GadgetBridge to restart

## Limitations
- The script only imports activity data from the `cardioActivities.csv` file into the `BASE_ACTIVITY_SUMMARY` table and copies and renames the GPX track (if included in the Runkeeper backup) into the `files/` folder
- The script does not import any data from `heartRate.csv`, `measurements.csv` or `steps.csv`
- The script only supports a limited set of activity keys (see `map_sport(sport)`)
	+ Add your own activity keys if needed, check `BASE_ACTIVITY_SUMMARY.ACTIVITY_KIND` in your `Gadgetbridge` SQLite database for valid keys
	
## Disclaimer
Runkeeper is a brand by ASICS. Neither the author nor this script is associated with Runkeeper or ASICS in any kind.
