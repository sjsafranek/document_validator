import cv2
import shapely
from shapely.geometry import LineString
import networkx

import lib


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



def getNeighbors(source, words):
    # remove source word
    words = [word for word in words if word.id != source.id]

    # TOP
    options = []
    for target in words:
        bounds = target.bbox.bounds
        if source.centroid.x >= bounds[0] and source.centroid.x <= bounds[2]:
            if (source.centroid.y <= target.centroid.y):
                options.append(target)
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # BOTTOM
    options = []
    for target in words:
        bounds = target.bbox.bounds
        if source.centroid.x >= bounds[0] and source.centroid.x <= bounds[2]:
            if (source.centroid.y >= target.centroid.y):
                options.append(target)
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]

    # RIGHT
    options = []
    for target in words:
        bounds = target.bbox.bounds
        if source.centroid.y >= bounds[1] and source.centroid.y <= bounds[3]:
            if (source.centroid.x <= target.centroid.x):
                options.append(target)
    if 0 != len(options):
        ordered = sorted(options, key=lambda target: shapely.distance(source.centroid, target.centroid))
        yield ordered[0]
    
    # LEFT 
    options = []
    for target in words:
        bounds = target.bbox.bounds
        if source.centroid.y >= bounds[0] and source.centroid.y <= bounds[3]:
            if (source.centroid.x >= target.centroid.x):
                options.append(target)
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

        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = lib.normalizeText(data['text'][i])
            confidence = data['conf'][i]
            if not text:
                continue
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            xmin = x
            ymin = y
            xmax = x + w
            ymax = y + h
            bbox = shapely.box(xmin, ymin, xmax, ymax)

            self.words[i] = Word(i, text, confidence, bbox)
            if text not in self.occurances:
                self.occurances[text] = []
            self.occurances[text].append(i)

        for source in self.words.values():
            words = [word for word in self.words.values() if word.id != source.id]
            for target in getNeighbors(source, words):
                distance = source.centroid.distance(target.centroid)
                # print(source, target, distance)
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
    data = lib.parseImage(image)
    datasource = Datasource(data)
    path = datasource.findShortestPath("super", "melee")
    print([word.text for word in path[0]])
    break
