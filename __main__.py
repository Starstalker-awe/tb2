from helpers import settings
from .web import app
import subprocess
import logging

logging.basicConfig(format=settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(settings.LOGGING_LEVEL)