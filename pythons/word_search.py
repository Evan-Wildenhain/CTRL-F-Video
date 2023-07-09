import json
import re
import pickle
from g2p_en import G2p
from similar_words import *
from store_similar import *
import threading
import time


def getPhraseTimestamps(phrase,file):
    """
    Returns timestamps of a phrase from a dictionary created from the given json.

    Args:
        phrase (list): List of strings representing words to search.
        file (str): File path to create the dictionary from.

    Returns:
        list: 4-element list with first element being list of timestamps, rest are empty lists.
              If any word from phrase is not in the dictionary, returns all empty lists.
    """
    words = createDictionary(file)
    searches = []
    times = []
    print(phrase)

    #all words exist in the dict
    for word in phrase:
        if word not in words:
            return [[],[],[],[]]
        
   

    previous = [x for x in words[phrase[0]]]
    #finds the intersections of words where the id is curr id-1, since we order each word
    # in the translation
    #e.g. this is a test -> (11, this) (12, is) (13, a) (14, test) would be a match
    for word in phrase[1:]:
        current = [x for x in words[word]]
        curr_dict = {id2-1: time2 for id2, time2 in current}
        result = [(id1+1, time1) for id1,time1 in previous if id1 in curr_dict]
        previous = result

    times = [r[1] for r in result]
    return [times,[],[],[]]

def getSingleWordTimestamps(word,file, pkl_file, model):
    """
    Returns timestamps of a single word from a dictionary created from a json,
    including exact, extended, phoneme, and similar matches.

    Args:
        word (list): List containing a single string representing a word to search.
        file (str): Json file path to create the dictionary from.
        pkl_file (str): File path to a pickle file containing phonetic keys of current video.
        model (model): A model to find similar sounding words.

    Returns:
        list: A list of four lists. Each list contains timestamps corresponding to:
              [exact matches, extended matches, phoneme matches, similar phonemes]
    """
    g2p = G2p()
    phonetic_conversion = tuple(g2p(word[0]))
    with open(pkl_file, 'rb') as f:
        phonetic_keys = pickle.load(f)
    
    words= createDictionary(file)
    exact_matches = []
    extended_matches = []
    phoneme_matches = []
    similar_phonemes = []

    identical_phonemes_search = findIdenticalPhonetics(word=word[0],phonetic_keys=phonetic_keys, words=words, phonetic_conversion=phonetic_conversion)
    extended_words_search,exact_search  = findWordAndExtendedWords(word=word[0], words=words)
    similar_search = findSimilarsoundingWords(phonetic_keys, phonetic_conversion, model)

    #combine all sets (remove duplicates)
    all_searches = identical_phonemes_search | extended_words_search | exact_search | similar_search

    store_thread = threading.Thread(target=storeSimilar, args=(word[0],all_searches,g2p,phonetic_conversion))
    store_thread.start()


    print("ALL", all_searches)

    while all_searches:
        search = all_searches.pop()
        for t in words[search]:
            if search == word[0]:
                exact_matches.append(t[1])
            elif search in identical_phonemes_search:
                phoneme_matches.append(t[1])
            elif search in extended_words_search:
                extended_matches.append(t[1])
            elif search in similar_search:
                similar_phonemes.append(t[1])

        
    return [exact_matches,extended_matches,phoneme_matches, similar_phonemes]



def createDictionary(file):
    """
    Reads a JSON file and creates a dictionary with words as keys and their timestamps as values.

    Args:
        file (str): File path to a JSON file containing segmented words and their timestamps.

    Returns:
        dict: A dictionary where each key is a word (after removing punctuation and converting to lower case) 
              and the value is a list of tuples. Each tuple contains an ID and the timestamp of the word.
    """
    f = open(file)
    json_data = json.load(f)
    segments = json_data["segments"]
    #key: word, value:[(id,timestamp),(id,timestamp)]
    timestamps = {}
    val = 0
    for segment in segments:
        for word in segment["words"]:
            #remove all the punctuation and stuff like that then lower all text.
            text = re.sub(r'[^\w\s\d]+', '', word["text"])
            text = text.lower()
            if text not in timestamps:
                timestamps[text] = []
            timestamps[text].append((val,word["start"]))
            val += 1
    return timestamps
