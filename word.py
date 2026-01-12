import utils


class Word(object):

    def __init__(self, id, text, confidence, bbox):
        self.id = id
        self.raw = text
        self.clean = utils.normalizeText(text)
        self.confidence = confidence
        self.bbox = bbox

    @property
    def text(self):
        return self.clean

    @property
    def centroid(self):
        return self.bbox.centroid

    def __str__(self):
        return f'{self.text} ({self.id})'

