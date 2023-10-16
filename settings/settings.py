import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

URL_TO_GET_RANDOM_HTML_WITH_IMG = 'https://c.xkcd.com/random/comic/'
SIZE_CHUNKED = 1024
COUNT_WORKER = 3
SAVE_IMG_PATH = os.path.join(BASE_DIR, 'comics')
TIMEOUT_SESSION = 2
