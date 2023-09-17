from dotenv import dotenv_values as load_env
from dotmap import DotMap
import logging
import cs50
import os

wd = os.getcwd().split('/')
while wd[-1] != 'tb2': wd = wd[0:-1]
wd = '/'.join(wd)

DB = cs50.SQL(f"sqlite:///{wd}/data.db")

ENV = DotMap(load_env(f"{wd}/.env"))

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