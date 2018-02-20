"""
checkbook.py
    Check the book's price and save it to specified output file ("/output.txt" by default)

Usage:
    python checkbook.py path/file.txt
"""

from BeautifulSoup import BeautifulSoup as bs
import urlparse
from urllib2 import urlopen
from urllib import urlretrieve
from difflib import SequenceMatcher
import codecs
import os
import sys

# Store a book entity
class Book:
    seq = 0
    objects = []
    
    def __init__(self, name, author, price):
        self.id = None
        self.name = name
        self.author = author
        self.price = price
        
        self.__class__.seq += 1
        self.id = self.__class__.seq
        self.__class__.objects.append(self)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return '<{}: {} - {} - {} - R$ {}>\n'.format(self.__class__.__name__, self.id, self.name, self.author, self.price)
    # < necessary to iterate through object
    def __iter__(self):
        return iter(self.objects)
        
    def __len__(self):
        return len(self.objects)
    
    def __getitem__(self, item):
        return self.objects[item]
    # necessary to iterate through object />
    def toString(self):
        return '{:45s}|{:25s}|{}\n'.format(self.name[:45], self.author[:25], self.price).decode(sys.stdout.encoding)
    
    @classmethod
    def reset(cls):
        cls.objects = []
    
    @classmethod
    def all(cls):
        return cls.objects
        
# Responsible to navigate, download and parse the html in order to find the prices
def main(bookname, out_file):
    """Downloads all the images at 'url' to /test/"""
    # url builder
    url = 'http://busca.saraiva.com.br/?q=';
    for word in bookname.split():
        url += word + '%20';
    print "Url: %s" % url
    
    # html parser
    soup = bs(urlopen(url))
    parsed = list(urlparse.urlparse(url))
    
    Book.reset()
    
    for item in soup.findAll("div", { "class" : "cs-list-container" }):
        # get the product's name and compare it to the bookname
        name_container = item.find("a" , { "class" : "cs-product" })
        if name_container is not None:
            name = name_container.contents[0].encode(sys.stdout.encoding, errors='replace')
            #print name.contents[0].encode(sys.stdout.encoding, errors='replace')
            if (similar(bookname, name)) > 0.7:
                # if it is similar then get its price
                # get the author first
                author_container = item.find("span" , { "class" : "cs-subtitle" })
                if author_container is not None:
                    author = author_container.contents[0].encode(sys.stdout.encoding, errors='replace')
                    # then get the price 
                    price_container = item.find("span" , { "class" : "cs-price-value" })
                    price = price_container.find("span").contents[0].encode(sys.stdout.encoding, errors='replace')
                    #print "Price is: R$ %s" % price.contents[0].encode(sys.stdout.encoding, errors='replace')
                    # Add the new book!!
                    Book(name, author, price)
    
    print(Book.all())
    # Get the biggest similarity string according the book's name and write to file
    similarity = 0
    book = None
    for temp in Book.objects:
        aux = similar(bookname, temp.name)
        if aux > similarity:
            similarity = aux
            book = temp
    
    if book is not None:
        # Save it to output file
        with codecs.open(out_file, "a", "utf-8-sig") as file:
            file.write(book.toString())
            file.close()
    

def _usage():
    print "usage: python checkbook.py path/file.txt"

# how much two strings are similar (0.0 <-> 1.0)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        _usage()
        sys.exit(-1)
    
    # TODO - Accept book's name instead of input filename
    #bookname = ' '.join(sys.argv[1:])
    filepath = sys.argv[1]
    out_file="output.txt"
    
    # Clean old output file
    try:
        os.remove(out_file)
    except:
        pass
        
    for bookname in open(filepath, 'r'):
        main(bookname, out_file)