"""
author: 
    Daniel Victoriano (@djose1164)
Copyright 2022 Cara

This module is for handling the interaction with the database.

Attributes:
    db (SqlAlchemy): Module variable to interact with database.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
