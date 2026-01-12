import re

import networkx
import shapely
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.strtree import STRtree

import utils
import geo
from word import Word
from logger import logger


class Datasource(object):
    
    def __init__(self, data):
        self.words = {}
        self.occurrences = {}

        logger.debug('collecting words')
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = data['text'][i]
            if not text:
                continue            
            confidence = data['conf'][i]
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            xmin = x
            ymin = y - h
            xmax = x + w
            ymax = y        
            bbox = shapely.box(xmin, ymin, xmax, ymax)

            word = self._addToken(text, confidence, bbox)
            if word.text not in self.occurrences:
                self.occurrences[word.text] = []
            self.occurrences[word.text].append(word.id)

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
            for target in geo.getNeighbors(source, self.spatial_index, words_list, self.bounds):
                distance = source.centroid.distance(target.centroid)
                self.graph.add_edge(source.id, target.id, weight=distance)

    def _addToken(self, text, confidence, bbox):
        i = len(self.words.values()) + 1
        self.words[i] = Word(i, text, confidence, bbox)
        return self.words[i]

    def findShortestPath(self, start: str, end: str):

        if ' ' in start:
            raise ValueError('TODO')
        if ' ' in end:
            raise ValueError('TODO')

        start = utils.normalizeText(start)
        end = utils.normalizeText(end)

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

    def getTokensByPattern(self, pattern):
        for token in self.occurrences:
            match = re.match(pattern, token)
            if match:
                yield token

