import logging
import threading

from time import sleep

HEARTBEAT = 0.5


def update_config():
    logging.info("Update config start")
    sleep(0.1)
    logging.info("Update config stop")


def manage_songs(name):
    while True:
        logging.info("Thread %s: running", name)
        sleep(5)


def update_game_info_and_setlist(name):
    while True:
        logging.info("Thread %s: running", name)
        sleep(1)


if __name__ == "__main__":
    my_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=my_format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : before creating any thread")

    manage_songs_thread = threading.Thread(target=manage_songs,
                                           args=("manage_songs_thread",))
    logging.info("Main    : starting - manage_songs_thread")
    manage_songs_thread.start()

    update_game_info_and_setlist_thread = threading.Thread(target=update_game_info_and_setlist,
                                                           args=("update_game_info_and_setlist_thread",))
    logging.info("Main    : starting - update_game_info_and_setlist_thread")
    update_game_info_and_setlist_thread.start()

    # while True:
        # logging.info("Main    : all done")
        # sleep(HEARTBEAT)

    # while True:
    #     logging.warning("Main    : -------------------------------")
    #     logging.warning("Main    : New iteration started ---------")
    #     logging.warning("Main    : -------------------------------")
    #
    #     sleep(HEARTBEAT)
    #
    #     update_config()
    #
    #     # logging.info("Main    : manage_songs_thread isAlive: %s", manage_songs_thread.isAlive())
    #     # logging.info("Main    : update_game_info_and_setlist_thread isAlive: %s", update_game_info_and_setlist_thread.isAlive())
    #
    #     # logging.info("Main    : before running thread - manage_songs_thread")
    #     # if not manage_songs_thread.is_alive():
    #     logging.info("Main    : starting - manage_songs_thread")
    #     manage_songs_thread.start()
    #     # logging.info("Main    : wait for the thread to finish")
    #     # manage_songs_thread.join()
    #
    #     # logging.info("Main    : before running thread - update_game_info_and_setlist_thread")
    #     # if not update_game_info_and_setlist_thread.is_alive():
    #     logging.info("Main    : starting - update_game_info_and_setlist_thread")
    #     update_game_info_and_setlist_thread.start()
    #     # logging.info("Main    : wait for the thread to finish")
    #     # update_game_info_and_setlist_thread.join()
    #
    #     logging.info("Main    : all done")
