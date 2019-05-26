"""
Configuration for logs
"""
import logging as logger
from resources.config import Config as config

# basic logging to file
logger.basicConfig(
    filename=config.log_directory,
    level=logger.DEBUG,
    format="%(asctime)s: %(name)-12s: %(levelname)-8s:%(message)s",
)

# set up logging to console
console = logger.StreamHandler()
console.setLevel(logger.DEBUG)
formatter = logger.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logger.getLogger('').addHandler(console)
logger = logger.getLogger(__name__)
