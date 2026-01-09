# import itertools

import cv2
import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
import networkx
# from numba import njit

import lib
from logger import logger


infile = 'MagicTheGathering_IsTuringComplete.pdf'


# PATH_WORDS_THRESHOLD = 5
# DISTANCE_THRESHOLD = width * 0.25


def display(image, data):
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        text = data['text'][i]
        confidence = data['conf'][i]
        if not text:
            continue
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
    cv2.imshow('img', image)
    cv2.waitKey(0)


# @njit
def getIntersections(line, words):
    return [word for word in words if line.intersects(word.bbox)]



def getNeighbors(source, words):
    # remove source word
    words = [word for word in words if word.id != source.id]

    bounds = MultiPolygon([word.bbox for word in words]).bounds
    minx = bounds[0]
    miny = bounds[1]
    maxx = bounds[2]
    maxy = bounds[3]

    # TOP
    line = LineString([source.centroid, Point(source.centroid.x, maxy)])
    options = [word for word in getIntersections(line, words)]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # BOTTOM
    line = LineString([source.centroid, Point(source.centroid.x, miny)])
    options = [word for word in getIntersections(line, words)]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # RIGHT
    line = LineString([source.centroid, Point(maxx, source.centroid.y)])
    options = [word for word in getIntersections(line, words)]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]
    
    # LEFT
    line = LineString([source.centroid, Point(minx, source.centroid.y)])
    options = [word for word in getIntersections(line, words)]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]



class Word(object):

    def __init__(self, id, text, confidence, bbox):
        self.id = id
        self.text = text
        self.confidence = confidence
        self.bbox = bbox

    @property
    def centroid(self):
        return self.bbox.centroid

    def __str__(self):
        return f'{self.text} ({self.id})'



class Datasource(object):
    
    def __init__(self, data):
        self.words = {}
        self.occurances = {}
        self.graph = networkx.Graph()

        logger.debug('collecting words')
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = lib.normalizeText(data['text'][i])
            confidence = data['conf'][i]
            if not text:
                continue
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            xmin = x
            ymin = y - h
            xmax = x + w
            ymax = y        
            bbox = shapely.box(xmin, ymin, xmax, ymax)

            self.words[i] = Word(i, text, confidence, bbox)
            if text not in self.occurances:
                self.occurances[text] = []
            self.occurances[text].append(i)

        logger.debug('building graph')
        for source in self.words.values():
            words = [word for word in self.words.values() if word.id != source.id]
            for target in getNeighbors(source, words):
                distance = source.centroid.distance(target.centroid)
                self.graph.add_edge(source.id, target.id, weight=distance)

    def findShortestPath(self, start: str, end: str):
        start = lib.normalizeText(start)
        end = lib.normalizeText(end)

        if start not in self.occurances:
            return None
        if end not in self.occurances:
            return None

        paths = []
        for s in self.occurances[start]:
            for e in self.occurances[end]:
                paths.append(self._findShortestPath(s, e))
        if 0 == len(paths):
            return None
        ordered = sorted(paths, key=lambda path: path[1])
        return ordered[0]

    def _findShortestPath(self, start: int, end: int):
        path = networkx.shortest_path(self.graph, source=start, target=end, weight="weight")
        words = [self.words[wordId] for wordId in path]
        line = LineString([word.centroid for word in words])
        distance = line.length
        return words, distance


for image in lib.readPdfPagesAsArray(infile):
    logger.debug('reading page')
    data = lib.parseImage(image)
    
    logger.debug('building datasource')
    datasource = Datasource(data)
    
    logger.debug('finding path')

    #phrase = 'Magic The Gathering'

    path = datasource.findShortestPath("super", "melee")
    print([word.text for word in path[0]])
    # print(dir(path[0][0].centroid))

    # path = datasource.findShortestPath("Magic", "Gathering")
    # print([word.text for word in path[0]])
    # print(dir(path[0][0].centroid))
    
    break
