#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId
from pprint import pprint


def getDb():
    client = MongoClient('mongodb://localhost:27017/')
    return client.video_analysis


def insert(collectionName, data):
    collection = getattr(getDb(), collectionName)
    collection.insert_one(data)


def getCollection(collectionName):
    return getattr(getDb(), collectionName)


def printCollection(collectionName):
    collection = getCollection(collectionName)
    cursor = collection.find()
    for document in cursor:
        pprint(document)


def getDocumentById(collectionName, id):
    collection = getCollection(collectionName)
    return collection.find_one({"_id" : ObjectId(id)})


def printDocumentById(collectionName, id):
    document = getDocumentById(collectionName, id)
    pprint(document)


def getDocumentByName(collectionName, name):
    collection = getCollection(collectionName)
    return collection.find_one({"name" : name})


def printDocumentByName(collectionName, name):
    document = getDocumentByName(collectionName, name)
    pprint(document)
