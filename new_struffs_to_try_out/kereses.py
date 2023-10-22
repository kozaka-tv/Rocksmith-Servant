from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Simple Ratio
print(fuzz.ratio("this is a test", "this is a test!"))  # 97

print(fuzz.partial_ratio("this is a test", "this is a test!"))  # 100

# Partial Ratio
print(fuzz.partial_ratio("this is a test", "this is a test!"))  # 100
# Token Sort Ratio
print(fuzz.ratio("fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear"))  # 91
print(fuzz.token_sort_ratio("fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear"))  # 100

# Token Set Ratio
print(fuzz.token_sort_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear"))  # 84
print(fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear"))  # 100

# Process
choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
print(process.extract("new york jets", choices, limit=2))  # [('New York Jets', 100), ('New York Giants', 78)]
print(process.extractOne("cowboys", choices))  # ("Dallas Cowboys", 90)
# You can also pass additional parameters to extractOne method to make it use a specific scorer.
# A typical use case is to match file paths:
t
# process.extractOne("System of a down - Hypnotize - Heroin", songs)
# ('/music/library/good/System of a Down/2005 - Hypnotize/01 - Attack.mp3', 86)
# process.extractOne("System of a down - Hypnotize - Heroin", songs, scorer=fuzz.token_sort_ratio)
# ("/music/library/good/System of a Down/2005 - Hypnotize/10 - She's Like Heroin.mp3", 61)
