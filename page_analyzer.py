import re
import itertools

import networkx
import shapely
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.strtree import STRtree

import ocr
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


class PageAnalyzer(object):
    
    def __init__(self, image):
        logger.debug('running ocr on page')
        data = ocr.read(image)

        self.shape = image.shape
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
        words = [self.getWordById(token_id) for token_id in path]
        line = LineString([word.centroid for word in words])
        distance = line.length
        return words, distance

    def getWordById(self, token_id):
        if token_id in self.words:
            return self.words[token_id]
        return None

    def getTokensByPattern(self, pattern):
        for word in self.words.values():
            if word.text == pattern:
                yield word
            elif word.raw == pattern:
                yield word
            elif re.match(pattern, word.text):
                yield word
            elif re.match(pattern, word.raw):
                yield word                
        # for token in self.occurrences:
        #     if token == pattern:
        #         for token_id in self.occurrences[token]:
        #             yield self.getWordById(token_id)
        #         continue
        #     match = re.match(pattern, token)
        #     if match:
        #         for token_id in self.occurrences[token]:
        #             yield self.getWordById(token_id)

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

        # groups = []
        # tokens = []
        # for token in self._getTokensFromText(text):
        #     words = [word for word in self.getTokensByPattern(token)]
        #     if 0 == len(words):
        #         return None
        #     groups.append([word.id for word in words])
        #     tokens += [word.text for word in words]
        # cleaned = ' '.join(tokens)

        if 0 == len(tokens):
            return

        if ' ' not in cleaned:
            for group in groups:
                yield [self.getWordById(group[0])], 0
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
            
            begins = []
            if type(args[0]) is Word:
                begins = [(args[0],)]
            elif type(args[0]) is str:
                begins = [item for item, _ in self._search(args[0])]
            
            ends = []
            if type(args[1]) is Word:
                ends = [(args[1],)]
            elif type(args[1]) is str:
                ends = [item[0] for item, _ in self._search(args[1])]
            elif type(args[1]) is list:
                for item in args[1]:
                    if type(item) is Word:
                        ends.append((item,))
                    elif type(item) is str:
                        ends += [item for item, _ in self._search(item)]

            for begin in begins:
                for end in ends:
                    path, distance = self._findShortestPath(begin[0].id, end[0].id)
                    results.append((path, distance))

            # for begin in begins:
            #     print(args[0], args[1])
            #     for neighbor in args[1]:
            #         for end, _ in self._search(neighbor):
            #             path, distance = self._findShortestPath(begin[0].id, end[0].id)
            #             results.append((path, distance))
            return results

'''

distance threshold
 - font size --> bbox size
 - page width


'''