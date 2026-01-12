

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

