#!/usr/bin/env python

from flask import Flask, jsonify, request, abort, send_from_directory
from bson.objectid import ObjectId
from utils.log import log


import json
import isbntools
import sys, time, pymongo

app = Flask(__name__, static_url_path='')

log("Beginning.")

db_host = 'localhost'
db_port = 27017

dbclient = pymongo.MongoClient(db_host, db_port)
db = dbclient['c-lib']
books = db['books']

log("Preparing routes.")

@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/c-lib/api/v1.0/books', methods=['GET'])
def get_books():
    results = []
    for doc in books.find():
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return jsonify({'books': results})


@app.route('/c-lib/api/v1.0/books/<string:book_id>', methods=['GET'])
def get_book_details(book_id):
    result = books.find_one({"_id": ObjectId(book_id)})
    result["_id"] = str(result["_id"])
    return jsonify({'details': result})


@app.route('/c-lib/api/v1.0/books', methods=['POST'])
def add_book():

    isbnservice = "wcat"

    request.get_data()

    try:
        jsonstuff = json.loads(request.data)
    except Exception as e:
        log("JSON Decoding fail: ", e, request.data)

    if not jsonstuff or not 'isbn' in jsonstuff or \
            isbntools.notisbn(jsonstuff['isbn']):
        log("Invalid ISBN: ", jsonstuff)
        return jsonify({'status': "INVALID ISBN"}), 400
    else:
        isbn = str(jsonstuff['isbn'])

    log("ISBN entered:", isbn)

    book = books.find_one({"isbn": isbn})
    if book:
        log("Book already entered")
        book['_id'] = str(book['_id'])
        return jsonify({'book': book, 'status': 'existant'}), 201

    try:
        meta = isbntools.meta(isbn, service=isbnservice)
        log("META found:", meta)
    except Exception as e:
        log("META not found: ", e)
        meta = {'Publisher': "Unknown",
                'Language': "Unknown",
                'Title': "Unkown",
                'Authors': ["Unkown"],
                'Year': "Unkown"}
    book = {
               'isbn': isbn,
               'publisher': meta['Publisher'],
               'language': meta['Language'],
               'title': meta['Title'],
               'authors': meta['Authors'],
               'year': meta['Year'],
               'created': time.time(),
               'modified': time.time(),
               'coordinates': (0, 0),
               'status': False,
               'tags': [],
               'comment': "",

           }

    log(book)
    books.insert(book)
    book['_id'] = str(book['_id'])
    return jsonify({'book': book, 'status': 'created'}), 201

log("Preparation done.")

if __name__ == '__main__':
    app.run(debug=True)
