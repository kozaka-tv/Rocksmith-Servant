import os
import re
from collections import defaultdict

# Path to the 'setlist' directory
SETLIST_DIR = "../setlist/"
OUTPUT_FILE = "../song_count_by_year_and_title.txt"

# Dictionary to store song play counts by year
# For each year, we will store a dictionary of songs and their counts.
year_song_counts = defaultdict(lambda: defaultdict(int))

# Updated regular expression to extract the year from filenames
year_pattern = re.compile(r"setlist_(\d{4})-\d{2}-\d{2}")

# Iterate over files in the 'setlist' directory
for filename in os.listdir(SETLIST_DIR):
    filepath = os.path.join(SETLIST_DIR, filename)
    if os.path.isfile(filepath):
        # Extract the year from the filename
        match = year_pattern.search(filename)
        if match:
            year = match.group(1)  # Extract the year (first capture group)

            # Open the file and read its content
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    # Clean up the song line (remove extra spaces, newlines, etc.)
                    song = line.strip()

                    # Skip unwanted lines
                    if not song or song.startswith("---------") or song.startswith("Setlist of"):
                        continue

                    # Avoid empty lines
                    if song:
                        # Increment the count for this song in the respective year
                        year_song_counts[year][song] += 1

# Write summarized data to the output file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for year, songs in sorted(year_song_counts.items()):  # Sort years
        f.write(f"Year: {year}\n")
        f.write("Song\tCount\n")
        f.write("------------------------\n")
        for song, count in sorted(songs.items(), key=lambda x: x[1], reverse=True):  # Sort songs by count
            f.write(f"{song}\t{count}\n")
        f.write("\n")  # Add a newline between years

print(f"Song play counts by year have been saved to {OUTPUT_FILE}")
