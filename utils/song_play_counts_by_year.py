import os
import re
from collections import defaultdict

# Path to the 'setlist' directory
SETLIST_DIR = "../setlist/"
OUTPUT_DIR = "../statistics/song_count_by_year"  # Directory to store the yearly output files

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

# Write summarized data to separate files for each year
for year, songs in year_song_counts.items():
    # Set the output file name for the current year
    output_file = os.path.join(OUTPUT_DIR, f"song_count_{year}.txt")

    # Calculate the total number of songs played in the year
    total_songs_played = sum(songs.values())

    # Calculate the number of distinct songs played
    distinct_songs_count = len(songs)

    # Write song play counts for the current year
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Year: {year}\n")
        f.write(f"Total songs played: {total_songs_played}\n")  # Add the total played songs
        f.write(f"Distinct songs played: {distinct_songs_count}\n")  # Add the distinct song count
        f.write("Count | Song\n")
        f.write("------------------------\n")
        for song, count in sorted(songs.items(), key=lambda x: x[1], reverse=True):  # Sort songs by count
            f.write(f"{count:2} | {song}\n")  # Add leading space for numbers < 10
        f.write("\n")  # Add a newline at the end

print(f"Song play counts by year have been saved in the folder: {OUTPUT_DIR}")
