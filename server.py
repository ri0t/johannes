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
booksdb = db['books']
journaldb = db['journal']

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
    return jsonify({'details': result})

@app.route('/c-lib/api/v1.0/books/<string:book_id>', methods=['UPDATE'])
def update_book(book_id):

    book = {"_id": ObjectId(book_id)}
    log("Updating book with _id:", book_id)

    original = booksdb.find_one(book)

    log(request.form)
    details = dict(request.form)
    del(details['_id'])
    log("Updated record: ", details)


    log("Updating with: ", details)

    result = booksdb.update(book, details)

    journal('UPDATE', {'in': details, 'out': original})
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
        log("Book already entered")
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
    booksdb.insert(book)
    book['_id'] = str(book['_id'])

    journal('ADD', {'in': book, 'out': None})

    return jsonify({'book': book, 'status': 'Book created'}), 201

log("Preparation done.")

if __name__ == '__main__':
    app.run(debug=True)
