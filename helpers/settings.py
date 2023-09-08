import logging
import cs50
import os

DB = cs50.SQL(f"sqlite:///{os.getcwd()}/data.db")
CPU_THREADS = len(os.sched_getaffinity(0))

_levels = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "WARNING": logging.WARNING,
    "CRITITAL": logging.CRITICAL
}

_settings = {setting["name"]: setting["value"] for setting in DB.execute("SELECT * FROM setting")}

LOGGING_LEVEL = _levels[_settings["logging_level"]]
LOGGING_FORMAT = "%(ascitime)s%(level)s:%(module)s:%(message)s"
HASH_SETTINGS = {"rounds": 128, "digest_size": 41, "salt_size": 8}