#!/usr/bin/env python

from bson.objectid import ObjectId
from pprint import pprint
import json
import time
import pymongo

from flask import Flask, jsonify, request
from voluptuous import Schema, Optional, Required, Match

from utils.log import log
import isbntools


app = Flask(__name__, static_url_path='')

log("Beginning.")

db_host = 'localhost'
db_port = 27017

dbclient = pymongo.MongoClient(db_host, db_port)
db = dbclient['c-lib']
booksdb = db['books']
journaldb = db['journal']

book_schema = Schema({
    Optional('_id'): Match('^(?=[a-f\d]{24}$)(\d+[a-f]|[a-f]+\d)'),
    Required('authors'): unicode,
    Required('comment'): unicode,
    Required('coordinates'): [int, int],
    Required('created'): float,
    Required('isbn'): Match('^(97(8|9))?\d{9}(\d|X)$'),
    Required('language'): unicode,
    Required('modified'): float,
    Required('publisher'): unicode,
    Required('status'): unicode,  # TODO: DUH!
    Required('tags'): unicode,
    Required('title'): unicode,
    Required('year'): int
})

log("Preparing routes.")


def journal(activity, detail):
    what = {'t': time.time(),
            'a': str(activity),
            'd': detail,
    }
    journaldb.insert(what)
    log("Journal updated: ", activity)


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/c-lib/api/v1.0/books', methods=['GET'])
def get_books():
    results = []
    for doc in booksdb.find():
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return jsonify({'books': results})


@app.route('/c-lib/api/v1.0/journal', methods=['GET'])
def get_journal():
    results = []
    for doc in journaldb.find():
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return jsonify({'journal': results})


@app.route('/c-lib/api/v1.0/books/<string:book_id>', methods=['GET'])
def get_book_details(book_id):
    result = booksdb.find_one({"_id": ObjectId(book_id)})
    result["_id"] = str(result["_id"])
    pprint(result)
    log("Returning book search for", book_id)
    return jsonify({'details': result})


@app.route('/c-lib/api/v1.0/books/<string:book_id>', methods=['UPDATE'])
def update_book(book_id):
    book = {"_id": ObjectId(book_id)}
    log("Updating book with _id:", book_id)

    original = booksdb.find_one(book)

    log("Incoming json:", request.json)
    details = request.json

    del (details['_id'])
    log("Updated record: ", details)

    try:
        valid_book = book_schema(details)
        pprint(valid_book)
        log('Book validated.')
    except Exception as ve:
        log(ve)
        return jsonify({'error': unicode(ve), 'status': 'Error'}), 415

    log("Updating with: ", valid_book)

    result = booksdb.update(book, valid_book)

    journal('UPDATE', {'in': valid_book, 'out': original})

    return jsonify({'result': result})


@app.route('/c-lib/api/v1.0/books/delete/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    log("Deleting book with _id:", book_id)
    book = {"_id": ObjectId(book_id)}

    original = booksdb.find_one(book)

    result = booksdb.remove(book)

    journal('DELETE', {'in': None, 'out': original})
    return jsonify({'result': result})


@app.route('/c-lib/api/v1.0/books', methods=['POST'])
def add_book_by_isbn():
    isbnservice = "wcat"

    request.get_data()

    try:
        jsonstuff = json.loads(request.data)
    except Exception as e:
        log("JSON Decoding fail: ", e, request.data)

    if not jsonstuff or not 'isbn' in jsonstuff or \
            isbntools.notisbn(jsonstuff['isbn']):
        log("Invalid ISBN: ", jsonstuff)
        return jsonify({'status': "Invalid ISBN"}), 400
    else:
        isbn = str(jsonstuff['isbn'])

    log("ISBN entered:", isbn)

    book = booksdb.find_one({"isbn": isbn})
    if book:
        log("Book known")
        pprint(book)
        book['_id'] = str(book['_id'])

        return jsonify({'book': book, 'status': 'Book existant'}), 201

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
        # TODO: Allow/offer manual entry
        return jsonify({'status': "Metaserver lookup failed."}), 504

    try:
        book = {
            'isbn': isbn,
            'publisher': unicode(meta['Publisher']),
            'language': unicode(meta['Language']),
            'title': unicode(meta['Title']),
            'authors': str(meta['Authors']),
            'year': int(meta['Year']),
            'created': time.time(),
            'modified': time.time(),
            'coordinates': [0, 0],
            'status': u'None',
            'tags': [],
            'comment': u''
        }
    except TypeError:
        return jsonify({'error'}), 415

    log(book)

    try:
        valid_book = book_schema(book)
        pprint(valid_book)
        log('Book validated.')
    except Exception as ve:
        log(ve)
        return jsonify({'error': unicode(ve), 'status': 'Error'}), 415

    booksdb.insert(valid_book)
    valid_book['_id'] = str(valid_book['_id'])

    journal('ADD', {'in': valid_book, 'out': None})

    return jsonify({'book': book, 'status': 'Book created'}), 201


log("Preparation done.")

if __name__ == '__main__':
    app.run(debug=True)
