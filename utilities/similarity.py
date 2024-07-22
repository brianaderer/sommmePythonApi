import singleton as singleton
from pyxdameraulevenshtein import damerau_levenshtein_distance, normalized_damerau_levenshtein_distance
from pyxdameraulevenshtein import damerau_levenshtein_distance_seqs, normalized_damerau_levenshtein_distance_seqs


class Similarity:

    def __init__(self):
        self.s = singleton.Singleton()

    def dl_sim(self, st1, st2):
        return normalized_damerau_levenshtein_distance(st1, st2)

    def contains_each_other(self, st1, st2):
        return st1 in st2 or st2 in st1

    def elastic_sim(self, st1, st2):
        score = self.dl_sim(st1, st2)
        set1 = set(st1)
        set2 = set(st2)
        jaccard = self.jaccard_similarity(set1, set2)
        score = (score + (1-jaccard)) / 2
        if self.contains_each_other(st1, st2):
            score = score * (2/3)
        return score

    def jaccard_similarity(self, set1, set2):
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union
