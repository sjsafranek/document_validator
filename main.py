# import itertools

import cv2
import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.strtree import STRtree
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



def getIntersections(line, spatial_index, words_list):
    """Get words that intersect with the line using spatial index."""
    # Query spatial index
    result_indices = spatial_index.query(line)
    # Use indices to lookup words from words_list
    return [words_list[int(idx)] for idx in result_indices]



def getNeighbors(source, spatial_index, words_list, bounds):
    """Get neighbors using spatial index for efficient intersection queries."""
    minx, miny, maxx, maxy = bounds

    # TOP
    line = LineString([source.centroid, Point(source.centroid.x, maxy)])
    options = [word for word in getIntersections(line, spatial_index, words_list) if word.id != source.id]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # BOTTOM
    line = LineString([source.centroid, Point(source.centroid.x, miny)])
    options = [word for word in getIntersections(line, spatial_index, words_list) if word.id != source.id]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # RIGHT
    line = LineString([source.centroid, Point(maxx, source.centroid.y)])
    options = [word for word in getIntersections(line, spatial_index, words_list) if word.id != source.id]
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]
    
    # LEFT
    line = LineString([source.centroid, Point(minx, source.centroid.y)])
    options = [word for word in getIntersections(line, spatial_index, words_list) if word.id != source.id]
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
        self.occurrences = {}

        logger.debug('collecting words')
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = lib.normalizeText(data['text'][i])
            if not text:
                continue            
            confidence = data['conf'][i]
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            xmin = x
            ymin = y - h
            xmax = x + w
            ymax = y        
            bbox = shapely.box(xmin, ymin, xmax, ymax)

            # self.words[i] = Word(i, text, confidence, bbox)
            word = self._addWord(text, confidence, bbox)
            if text not in self.occurrences:
                self.occurrences[text] = []
            self.occurrences[text].append(word.id)

        # Create spatial index for efficient intersection queries
        # Keep words list in same order as bboxes for mapping
        logger.debug('creating spatial index')
        words_list = list(self.words.values())
        all_bboxes = [word.bbox for word in words_list]
        self.spatial_index = STRtree(all_bboxes)
        
        # Pre-compute document bounds once
        logger.debug('computing bounding box')
        self.bounds = MultiPolygon(all_bboxes).bounds

        # Build weighted graph
        logger.debug('building weighted graph')
        self.graph = networkx.Graph()
        for source in words_list:
            for target in getNeighbors(source, self.spatial_index, words_list, self.bounds):
                distance = source.centroid.distance(target.centroid)
                self.graph.add_edge(source.id, target.id, weight=distance)

    def _addWord(self, text, confidence, bbox):
        i = len(self.words.values()) + 1
        self.words[i] = Word(i, text, confidence, bbox)
        return self.words[i]

    def findShortestPath(self, start: str, end: str):
        start = lib.normalizeText(start)
        end = lib.normalizeText(end)

        if start not in self.occurrences:
            return None
        if end not in self.occurrences:
            return None

        paths = []
        for s in self.occurrences[start]:
            for e in self.occurrences[end]:
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



if __name__ == '__main__':    
    for image in lib.readPdfPagesAsArray(infile):
        logger.debug('reading page')
        
        data = lib.parseImage(image)
    
        logger.debug('building datasource')
        datasource = Datasource(data)
    
        logger.debug('finding path')

        #phrase = 'Magic The Gathering'

        path = datasource.findShortestPath("super", "melee")
        print([word.text for word in path[0]])
        
        print(datasource.occurrences.keys())

        break
