# -*- coding: utf-8 -*-
import bson
import json
import pymongo
from pymongo import MongoClient

class MongoTHK(object):
    def __init__(self, db, col, **kwargs):
        self._conn = MongoClient(**kwargs)
        self._db = db
        self._collection = col

        self.cursor = self._conn[db][col]

    def close(self):
        self._conn.close()
