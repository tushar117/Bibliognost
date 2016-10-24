import xml.etree.ElementTree as elTree
from urllib import parse

import requests

from . import grresponse
from Bibliognost import credentials


class GoodReads(object):
    def __init__(self, book_id):
        self.url = 'https://www.goodreads.com/book/show?{query_params}'
        self.query_params = parse.urlencode({'key': credentials['goodreads']['key'], 'id': book_id, 'format': 'xml'})
        self.response = requests.get(self.url.format(query_params=self.query_params))
        self.root = elTree.fromstring(self.response.content)
        self.book_node = self.root.find(grresponse.CORE_DATA_NODE_TAG)

    def get_core_data(self):
        core_data = dict()
        for node in grresponse.CORE_DATA_NODE_DESCENDENTS:
            text = self.book_node.find(node).text
            if text:
                core_data[node] = text
        return core_data

    def get_similar_books(self):
        """
        Returns a list of similar books for a book object

        :return: list containing goodreads book ids
        """
        similar_books = []
        similar_books_node = self.book_node.find(grresponse.SIMILAR_BOOKS_NODE_TAG)
        if similar_books_node:
            for book_node in similar_books_node.findall(grresponse.SIMILAR_BOOKS_NODE_CHILD):
                for node in grresponse.SIMILAR_BOOKS_NODE_CHILD_DESCENDENTS:
                    similar_books.append(book_node.find(node).text)
        return similar_books

    def get_authors(self):
        """
        Returns the authors dict for a book obj

        :return: dict, a dict with goodreads author id as key and another dict as val
        """
        authors = dict()
        authors_node = self.book_node.find(grresponse.AUTHORS_NODE_TAG)
        if authors_node:
            for author_node in authors_node.findall(grresponse.AUTHORS_NODE_CHILD):
                author_data = dict()
                for node in grresponse.AUTHORS_NODE_CHILD_DESCENDENTS:
                    author_data[node] = author_node.find(node).text
                if 'id' in author_data:
                    authors[author_data['id']] = author_data
        return authors

    def get_ratings(self):
        """
        Returns the ratings distribution for a book

        :return: string containing ratings distribution
        """
        ratings_node = self.book_node.find(grresponse.RATINGS_NODE_TAG)
        return ratings_node.find(grresponse.RATINGS_DIST_TAG).text or ''

    def get_book_data(self):
        """
        Returns all the relevent info for a book

        :return: dict
        """
        return dict(
            **self.get_core_data(),
            authors=self.get_authors(),
            similar_books=self.get_similar_books(),
            ratings_dist=self.get_ratings()
        )
