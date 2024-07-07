import singleton as singleton
from pyxdameraulevenshtein import damerau_levenshtein_distance, normalized_damerau_levenshtein_distance
from pyxdameraulevenshtein import damerau_levenshtein_distance_seqs, normalized_damerau_levenshtein_distance_seqs


class Similarity:

    def __init__(self):
        self.s = singleton.Singleton()

    def dl_sim(self, st1, st2):
        return normalized_damerau_levenshtein_distance(st1, st2)

    def jaccard_similarity(self, set1, set2):
        # intersection of two sets
        intersection = len(set1.intersection(set2))
        # Unions of two sets
        union = len(set1.union(set2))

        return intersection / union
