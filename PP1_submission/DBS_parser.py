
#FILE: skeleton_parser.py
#------------------
#Author: Firas Abuzaid (fabuzaid@stanford.edu)
#Author: Perth Charernwattanagul (puch@stanford.edu)
#Modified: 04/21/2014
#
#Skeleton parser for CS564 programming project 1. Has useful imports and
#functions for parsing, including:
#
#1) Directory handling -- the parser takes a list of eBay json files
#and opens each file inside of a loop. You just need to fill in the rest.
#2) Dollar value conversions -- the json files store dollar value amounts in
#a string like $3,453.23 -- we provide a function to convert it to a string
#like XXXXX.xx.
#3) Date/time conversions -- the json files store dates/ times in the form
#Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
#for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.
#
#Your job is to implement the parseJson function, which is invoked on each file by
#the main function. We create the initial Python dictionary object of items for
#you; the rest is up to you!
#Happy parsing!

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

def isJson(f):
    """
    Returns true if a file ends in .json
    """
    return len(f) > 5 and f[-5:] == '.json'

def transformMonth(mon):
    """
    Converts month to a number, e.g. 'Dec' to '12'
    """
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

def transformDttm(dttm):
    """
    Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
    """
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

def transformDollar(money):
    """
    Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
    """
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)





##############################################################################################
###################################### My functions and stuff ################################
#NULL constant
NULL = 'NULL'
#
# NOTE this is the schema which the parser currently output as. 
# Any thing in here that is NOT NULL is enforced by the parser
# NULL values in the table are output as the string 'NULL' (no quotes)
# It does not however enforce FORIEGN KEY constraints.
# Finally, there is no error handling, happy path only :)


#Categories (itemId Integer,
#Category VARCHAR NOT NULL, 
#FORIEGN KEY itemId REFERENCES Items(itemId) ON DELETE CASCADE, ON UPDATE CASCADE)

#Items (itemId Integer Primary Key,
# name VARCHAR NOT NULL,
# seller VARCHAR,
# description VARCHAR NOT NULL,
# currently Real NOT NULL,
# firstBid Real NOT NULL,
# buyPrice Real,
# numberBids Integer,
# started DATE NOT NULL,
# ends DATE,
# FORIEGN KEY seller REFERENCES Users (userId) ON UPDATE CASCADE)

# Users (userId VARCHAR PRIMARY KEY,
# rating REAL NOT NULL,
# country VARCHAR,
# location VARCHAR)

# Bids (itemId INTEGER,
# userId VARCHAR,
# time DATE NOT NULL,
# amount REAL NOT NULL
# FORIEGN KEY itemId REFERENCES Items(itemId) ON DELETE CASCADE ON UPDATE CASCADE
# FORIEGN KEY userId REFERENCES Users(userId) ON DELETE CASCADE ON UPDATE CASCADE)



class Database:
    '''
    Database is the main class containing all the entries for each table
    '''
    def __init__(self):
        #Users table data
        self._users = set()
        #Items table data
        self._items = set()
        #Bids table data
        self._bids = set()
        #Categories table data
        self._categories = set()

    def parse_file(self, fname):
        '''
        Open the file and pass each of the items in the file
        to _add_record

        :param fname: name of the file
        '''

        with open(fname, 'r') as ifs:
            items = loads(ifs.read())['Items']
            for rec in items:
                self._add_record(rec)
            print "Success parsing %s" % fname


    def _add_record(self, record):
        '''
        parse the item from the json file.

        :param record: an 'item' from a json file
        '''
        item_id = record['ItemID']

        #add the item to table
        self._items.add(Item(record))
        for cat in record['Category']:
            self._categories.add(Category(item_id,cat))
        
        #add the seller to users
        self._users.add(User.seller(record))
        if record['Bids'] != None:
            #add the bidders to users and bids to bids table
            for rec in record['Bids']:
                self._users.add(User.bidder(rec['Bid']['Bidder']))
                self._bids.add(Bid(item_id, rec['Bid']))

    def write_tables(self):
        '''
        write all the .dat files for users, items, bids and categories
        '''
        #write the user table
        with open(User.output, 'w') as out:
            for user in self._users:
                out.write(str(user))
        
        with open(Item.output, 'w') as out:
            for item in self._items:
                out.write(str(item))
        
        with open(Category.output, 'w') as out:
            for cat in self._categories:
                out.write(str(cat))

        with open(Bid.output, 'w') as out:
            for bid in self._bids:
                out.write(str(bid))

    @property
    def items(self):
        return self._items

    @property
    def users(self):
        return self._users


class User:
    '''
    user class is an entry in the user table.
    '''
    output = 'Users.dat'
    #row output format
    str_format = '"{0}"|{1}|"{2}"|"{3}"\n'
    def __init__(self, user_id, rating, country, location):
        '''
        DO NOT CALL THIS METHOD DIRECTLY. Use one of the class 
        method constructors
        '''
        self._user_id = user_id
        self._rating = rating
        self._country = country.replace('"', '""')
        self._location = location.replace('"', '""')

    
    @classmethod
    def seller(cls, record):
        '''
        parse the seller information, return User obj
        :param record: item
        '''
        user_id = record['Seller']['UserID']
        rating = record['Seller']['Rating']
        country = record['Country']
        location = record['Location']

        return cls(user_id, rating, country, location)

    @classmethod
    def bidder(cls, record):
        '''
        parse bidder information return User obj
        :param record: item['Bids'][i]['Bid']['Bidder']
        '''
        user_id = record['UserID']
        rating = record['Rating'] 
        country = record.get('Country', NULL)
        location = record.get('Location', NULL)

        return cls(user_id, rating, country, location)

    def __eq__(self, other):
        eq = self._user_id == other._user_id
        eq = eq and self._rating == other._rating
        eq = eq and self._country == other._country
        eq = eq and self._location == other._location
        return eq

    def __hash__(self):
        return hash(self._user_id)

    def __str__(self):
        return User.str_format.format(self._user_id,
                self._rating, self._country, self._location)

class Item:
    '''
    entry in the items table
    '''
    #output file Items table
    output = 'Items.dat'
    #row output format
    str_format = '{0}|"{1}"|"{2}"|"{3}"|{4}|{5}|{6}|{7}|{8}|{9}\n'
    def __init__(self, record):
        '''
        parse the Item 
        :param record: - item
        '''
        self._item_id = record['ItemID']
        self._name = record['Name'].replace('"', '""')
        self._seller = record['Seller']['UserID'].replace('"', '""')
        self._description = '' if  record['Description'] == None else record['Description'].replace('"', '""')
        self._currently = transformDollar(record['Currently'])
        self._first_bid = transformDollar(record['First_Bid'])
        self._buy_price = NULL if 'Buy_Price' not in record else transformDollar(record['Buy_Price'])
        self._number_bids = record['Number_of_Bids']
        self._started = transformDttm(record['Started'])
        self._ends = transformDttm(record['Ends'])
    
    def __str__(self):
        return Item.str_format.format(self._item_id, self._name, self._seller, self._description,
                self._currently, self._first_bid, self._buy_price, self._number_bids,
                self._started, self._ends)
    
    def __hash__(self):
        return hash(self._item_id)

    def __eq__(self, other):
        eq = self._item_id and other._item_id
        eq = eq and self._name and other._name
        eq = eq and self._seller and other._seller
        eq = eq and self._description and other._description
        eq = eq and self._currently and other._currently
        eq = eq and self._first_bid and other._first_bid
        eq = eq and self._buy_price and other._buy_price
        eq = eq and self._number_bids and other._number_bids
        eq = eq and self._started and other._started
        eq = eq and self._ends and other._ends
        return eq

class Bid:
    '''
    Entry in the bids table
    '''
    output = 'Bids.dat'
    #row output format
    str_format = '{0}|"{1}"|{2}|{3}\n'
    
    def __init__(self, item_id, record):
        '''
        :param item_id: the ItemID of the item being bid on
        :param record: item['Bids'][0]['Bid']
        '''

        self._item_id = item_id
        self._user_id = record['Bidder']['UserID'].replace('"', '""')
        self._time = transformDttm(record['Time'])
        self._amount = transformDollar(record['Amount'])


    def __str__(self):
        return Bid.str_format.format(self._item_id,
                self._user_id, self._time, self._amount)

    def __hash__(self):
        return hash(hash(self._item_id) + hash(self._user_id) + hash(self._amount))

    def __eq__(self, other):
        eq = self._item_id == other._item_id
        eq = eq and self._user_id == other._user_id
        eq = eq and self._amount == other._amount
        return eq

        
class Category:
    '''
    Entry in the categories table
    '''
    output = 'Categories.dat'
    #row output format
    str_format = '{0}|"{1}"\n'
    pass
    def __init__(self, item_id, category):
        '''
        :param item_id: the ItemID of the item in category
        :param category: category name of the item
        '''
        self._item_id = item_id
        self._category = category.replace('"', '""')


    def __str__(self):
        return Category.str_format.format(self._item_id, self._category)

    def __hash__(self):
        return hash(hash(self._item_id) + hash(self._category))

    def __eq__(self, other):
        return (self._item_id == other._item_id) and (self._category == other._category)

###############################################################################################################


def main(argv):
    """
    Loops through each json files provided on the command line and passes each file
    to the parser
    """
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    
    database = Database()
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            database.parse_file(f)
    
    database.write_tables()

if __name__ == '__main__':
    main(sys.argv)
