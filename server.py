#!/usr/bin/env python

from flask import Flask, jsonify, request, abort
from bson.objectid import ObjectId

import json
import isbntools
import sys, time, pymongo

app = Flask(__name__)

host = 'localhost'
port = 27017

books_list = [
    {
        'status': True,
        'tags': [],
        'comment': "",
        'coordinates': (0, 0),
        "Publisher": "Inventur-Verl.",
        "Language": "ger",
        "Title": "Sterbehilfe f\u00fcr Planeten ausgespielt",
        "Authors": [
            "Billa S."
        ],
        "ISBN-13": "3000085785",
        "Year": "2002"

    },
    {
        'status': False,
        'tags': [],
        'comment': "",
        'coordinates': (0, 0),
        'Publisher': '',
        'Language': '',
        'Title': '',
        'Authors': [],
        'ISBN-13': '3000085785',
        'Year': '2002'

    },
]

dbclient = pymongo.MongoClient(host, port)
db = dbclient['c-lib']
books = db['books']


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
        print("JSON Decoding fail: ", e, request.data)

    if not jsonstuff or not 'isbn' in jsonstuff or \
            isbntools.notisbn(jsonstuff['isbn']):
        abort(400)
    else:
        print(jsonstuff)
        isbn = str(jsonstuff['isbn'])

    print("ISBN entered:", isbn)

    if books.find_one({"isbn": isbn}) != None:
        abort(400)

    try:
        meta = isbntools.meta(isbn, service=isbnservice)
        print("META found:", meta)
    except Exception as e:
        print("META not found: ", e)
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

    print(book)
    books.insert(book)
    book['_id'] = str(book['_id'])
    return jsonify({'book': book}), 201

if __name__ == '__main__':
    app.run(debug=True)
