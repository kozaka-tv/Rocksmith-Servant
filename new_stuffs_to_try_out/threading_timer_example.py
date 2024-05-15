import logging
import threading
import time


def thread_function(name):
    logging.info("Thread %s: started", name)
    logging.info("Waiting 1 sec")
    time.sleep(1)
    logging.info("...Function done")


if __name__ == "__main__":
    while True:
        my_format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=my_format, level=logging.INFO,
                            datefmt="%H:%M:%S")

        logging.info("Main    : before creating thread")
        x = threading.Timer(3.0, thread_function, args=(1,))
        logging.info("Main    : before running thread")
        x.start()
        logging.info("Main    : wait for the thread to finish")
        x.join()
        logging.info("Main    : all done")
