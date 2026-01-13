import re
import itertools

import networkx
import shapely
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.strtree import STRtree

import utils
from word import Word
from logger import logger


def getWords(data):
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
        yield Word(i+1, text, confidence, bbox)


class Datasource(object):
    
    def __init__(self, data):
        self.words = {}
        self.occurrences = {}

        # Add words to occurences list
        logger.debug('collecting words')
        for word in getWords(data):
            self.words[word.id] = word
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
            for target in utils.getNeighbors(source, self.spatial_index, words_list, self.bounds):
                distance = source.centroid.distance(target.centroid)
                self.graph.add_edge(source.id, target.id, weight=distance)

    def findShortestPath(self, start: str, end: str):
        # Check for spaces
        if ' ' in start:
            raise ValueError('TODO')
        if ' ' in end:
            raise ValueError('TODO')
        paths = []
        for s in self._getTokenOccurances(start):
            for e in self._getTokenOccurances(end):
                paths.append(self._findShortestPath(s, e))
        if 0 == len(paths):
            return [], None
        ordered = sorted(paths, key=lambda path: path[1])
        return ordered[0]
        # return ordered

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

    def _getTokenOccurances(self, text):
        token = utils.normalizeText(text)
        if token not in self.occurrences:
            return []
        return self.occurrences[token]

    def _getTokensFromText(self, text):
        return [utils.normalizeText(part) for part in text.split(' ')]

    def _search(self, text):
        groups = []

        tokens = [] 
        for token in self._getTokensFromText(text):
            ids = self._getTokenOccurances(token)
            if not ids:
                return None
            groups.append(ids)
            tokens.append(token)
        cleaned = ' '.join(tokens)

        if 0 == len(tokens):
            return

        if ' ' not in cleaned:
            for group in groups:
                yield [self.words[group[0]]], 0
            return

        for combination in itertools.product(*groups):
            result = []
            total_distance = 0
            for pair in itertools.pairwise(combination):
                path, distance = self._findShortestPath(pair[0], pair[1])
                if 2 != len(path):
                    break
                if 0 == len(result):
                    result.append(path[0])
                result.append(path[1])
                total_distance += distance

            # check result
            found = ' '.join([item.text for item in result])
            if cleaned == found:
                yield result, total_distance

    def search(self, *args, **kwargs):
        if kwargs and kwargs['start'] and kwargs['end']:
            return self.findShortestPath(kwargs['start'], kwargs['end'])
        elif args and 1 == len(args):
            return [result for result in self._search(args[0])]
        elif args and 2 == len(args):
            results = []
            for begin, _ in self._search(args[0]):
                for neighbor in args[1]:
                    for end, _ in self._search(neighbor):
                        print(end)
                        path, distance = self._findShortestPath(begin[0].id, end[0].id)
                        results.append((path, distance))
            return results

