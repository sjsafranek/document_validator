import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.strtree import STRtree



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



def normalizeText(text):
    characters = [char.lower() for char in text if char.isalnum()]
    # characters = [char.lower() for char in text if not char.isspace()]
    if 0 == len(characters):
        return ''
    # if characters[-1] in '.,;!?':
        # characters = characters[:-1]
    normalized = "".join(characters)
    return normalized
