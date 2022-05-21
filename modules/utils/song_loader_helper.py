def replace_dlc_and_cdlc(file_name):
    return str(file_name).strip().replace('cdlc\\', '').replace('dlc\\', '')
