import logging
logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    # level=logging.WARNING,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Set the httpx and groq loggers to WARNING level
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import dotenv
dotenv.load_dotenv()
