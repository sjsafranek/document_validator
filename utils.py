
def normalizeText(text):
    # characters = [char.lower() for char in text if char.isalnum()]
    characters = [char.lower() for char in text if not char.isspace()]
    if 0 == len(characters):
        return ''
    if characters[-1] in '.,;!?':
        characters = characters[:-1]
    normalized = "".join(characters)
    return normalized
