# load data using Python JSON module
import json

import pandas as pd

# with open('multiple_levels.json', 'r') as f:
#     data = json.loads(f.read())
# # Normalizing data
# multiple_level_data = pd.json_normalize(data, record_path=['Results'],
#                                         meta=['original_number_of_clusters', 'Scaler', 'family_min_samples_percentage'],
#                                         meta_prefix='config_params_', record_prefix='dbscan_')
# # Saving to CSV format
# multiple_level_data.to_csv('multiplelevel_normalized_data.csv', index=False)

#RSPL
with open('../../modules/song_loader/rspl_example.json', 'r') as f:
    data = json.loads(f.read())
# Normalizing data
multiple_level_data = pd.json_normalize(data, record_path=['playlist'],
                                        meta=['dlc_set'],
                                        meta_prefix='config_params_', record_prefix='dbscan_')
# Saving to CSV format
multiple_level_data.to_csv('rspl_normalized_data.csv', index=False)

