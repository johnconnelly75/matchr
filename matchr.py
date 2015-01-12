__author__ = 'john'

import csv
from operator import itemgetter
import uuid
from pattern.metrics import similarity, levenshtein, LEVENSHTEIN, DICE
from fuzzywuzzy import fuzz
import nltk
import string


london = '<insert TARGET file>'
entities = '<insert PRIME file>'

def getPublicCompanies():
    pc = []
    with open(london, 'rb') as fin:
        fR = csv.reader(fin)
        fR.next()
        for row in fR:
            row = [x.strip() for x in row]
            pc.append(row[1])
            #print row[1]
    return pc

def getEntityCompanies():
    ec = []
    with open(entities, 'rb') as fin:
        fR = csv.reader(fin)
        fR.next()
        for row in fR:
            row = [x.strip() for x in row]
            #print row[34]
            if row[34] not in ec:
                ec.append(row[34])
    return ec

class Matching(object):
    """
    matching - should be able to take a word for word or row for row

    Test if word is same and/or how similar

    for word in [words,]:
        a = Matching(word, prime)
        score = a.score
    """

    def __init__(self, prime, target):
        self.prime = prime
        self.target = target

        self.score = self.score()

    def score(self):
        return float(self.match2words()) + float(self.fullMatch()) + float(self.firstPart())

    def match2words(self):
        lev1 = similarity(self.prime, self.target, metric=LEVENSHTEIN)
        #lev2 = levenshtein(self.prime, self.target)
        #lev3 = nltk.edit_distance(self.prime, self.target)
        di = similarity(self.prime, self.target, metric=DICE)

        score2 = fuzz.ratio(self.prime, self.target)
        score3 = fuzz.partial_ratio(self.prime, self.target)
        score1 = lev1 + di + score2 + score3

        score4 = fuzz.ratio(self.prime[:5], self.target[:5])

        return score1 + score4

    def firstPart(self):
        lenPrime = len(self.prime)
        lenTarget = len(self.target)
        if self.prime[:int(lenPrime*.5)] == self.target[:int(lenTarget*.5)]:
            return 100
        elif self.prime[:5] == self.target[:5]:
            return 50
        else:
            return 0


    def fullMatch(self):
        if self.prime == self.target:
            return 100
        else:
            return 0



class MatchingList(object):
    """
    takes two lists of single entities such as company lists, etc

    ultimately returns lists --> {primeWord1: {id: idNum, matches: [(id, targetWord1, score), (id, targetWord2, score)]},
                                    primeWord2: {id: idNum, matches: [(id, tW1, score), (id, tW2, score)]}}

    companyMatches = MatchingList(cxCompanies, londonCompanies)
    matches = companyMatches.match()

    b = {'Google':
             {'matches': [(UUID('2ea9e172-ec32-4442-ad5c-51a826745b77'), 'Google, Inc.', 176.31428571428572)],
              'id': UUID('8e913361-bf05-4f64-be69-21514bc64305')},
         'Microsoft, Inc.':
             {'matches':
                  [(UUID('1dd02f45-9e48-47c7-a05a-f09c52ca8e38'), 'Microsoft', 183.4923076923077)],
              'id': UUID('22db86d8-d376-4173-8a23-b07e2fbcc0ab')}}

    """

    def __init__(self, primeList, targetList):
        self.primeList = primeList
        self.targetList = targetList

        self.primeListIndex = ''
        self.targetListIndex = ''

        self.pLIDIndex = 0
        self.tLIDIndex = 0

        self.scoreThreshold = 150.00

        self.resultList = {}

    def idGenerator(self, row=None, SecOrPri='Prime'): #element=None,
        if row:
            if SecOrPri == 'Prime':
                return row[self.pLIDIndex]
            else:
                return row[self.tLIDIndex]
        else:
            return uuid.uuid4()

    def matchProcessing(self):
        # sorts the result lists and returns top 5 results
        pass

    def normalize(self, word):
        table = string.maketrans("","")
        word = word.translate(table, string.punctuation)
        return word.lower().strip()

    def match(self):
        """
        :return:
        returns the list
        """
        for primeElement in self.primeList:
            self.resultList[primeElement] = {'id': self.idGenerator()}
            print 'Finding a match for ', primeElement
            for targetElement in self.targetList:
                #print 'comparing', self.normalize(primeElement), self.normalize(targetElement)
                m = Matching(self.normalize(primeElement), self.normalize(targetElement))
                score = m.score
                row = [self.idGenerator(), targetElement, score]
                #if score > self.scoreThreshold:
                    #print '\t', primeElement, '---> ', targetElement
                try:
                    self.resultList[primeElement]['matches'].append(row)
                except KeyError, e:
                    self.resultList[primeElement]['matches'] = [row, ]
            newSortedList = sorted(self.resultList[primeElement]['matches'], key=itemgetter(2), reverse=True)
            self.resultList[primeElement]['matches'] = newSortedList
            for x in self.resultList[primeElement]['matches'][:5]:
                if x[-1] > 200.00:
                    print '\t', primeElement, '---> ', x[1:]
            print'___' * 100

    def getMatch(self):
        self.match()
        rL = self.resultList
        closest = {}
        for word, matchesID in rL.iteritems():
            matches = matchesID['matches']
            wordID = matchesID['id']
            #print word, wordID, matches
            for match in matches:
                if match[2] > self.scoreThreshold:
                    row = word, '---> ', match[1:]
                    print row
                    closest[word] = {'id': wordID}
                    if 'matches' in closest.keys():
                        closest[word]['matches'].append(match)
                    else:
                        closest[word]['matches'] = [match, ]
        return closest


class MatchProfile(object):
    """
    matches 2 rows and returns score for similiarity

    Need to figure out how to get element matching as well Name:Name, Company:Company

    """
    def __init__(self, row1, row2):
        self.rowPrime = row1
        self.rowTarget = row2

        self.elementPrime = ''
        self.elementTarget = ''

publicCompanies = getPublicCompanies()
cxEntities = getEntityCompanies()
m = MatchingList(cxEntities, publicCompanies)
m.scoreThreshold = 200.00
#m = MatchingList(['Google', 'Microsoft, Inc.'], ['Apple', 'Microsoft', 'what', 'Google, Inc.'])
a = m.getMatch()
print a


"""
Build a recommendation engine for proper matches
Have the program learn from what is a match and what isn't

"""