import utils


class Word(object):

    def __init__(self, word_id, text, confidence, bbox):
        self.id = word_id
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



class SearchResult(object):

    def __init__(self, page_number: int, path: list[Word], distance: float):
        self.page_number = page_number
        self.path = path
        self.distance = distance

    @property
    def text(self):
        return ' '.join([word.raw for word in self.path])

