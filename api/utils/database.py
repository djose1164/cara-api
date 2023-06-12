"""
author: 
    Daniel Victoriano (@djose1164)
Copyright 2022 Cara

This module is for handling the interaction with the database.

Attributes:
    db (SqlAlchemy): Module variable to interact with database.
"""
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import pytz

db = SQLAlchemy()


def SantoDomingoDatetime():
    tz = pytz.timezone("America/Santo_Domingo")
    time = dt.datetime.now(tz)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    return current_time
