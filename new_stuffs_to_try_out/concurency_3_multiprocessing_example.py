import multiprocessing
import time

import requests

SESSION = None


def set_global_session():
    global SESSION
    if not SESSION:
        SESSION = requests.Session()


def download_site(url):
    with SESSION.get(url) as response:
        name = multiprocessing.current_process().name
        print(f"{name}:Read {len(response.content)} from {url}")


def download_all_sites(sites):
    with multiprocessing.Pool(initializer=set_global_session) as pool:
        pool.map(download_site, sites)


if __name__ == "__main__":
    sites_to_download = [
                "https://www.jython.org",
                "http://olympus.realpython.org/dice",
            ] * 200
    start_time = time.time()
    download_all_sites(sites_to_download)
    duration = time.time() - start_time
    print(f"Downloaded {len(sites_to_download)} in {duration} seconds")
