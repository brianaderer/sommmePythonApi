import singleton

class Dependencies:
    dependencies = {
        'regions': ['countries'],
        'appellations': ['countries', 'regions']
    }

    correlations = {
        'producers': ['cuvees'],
        'cuvees': ['appellations', 'colors'],
        'appellations': ['regions', 'countries'],
        'regions': ['countries'],
        'skus': ['sizes', 'cases'],
        'colors': ['types', 'classes'],
        'types': ['classes'],
        'grapes': ['types', 'colors'],
    }

    def __init__(self):
        self.s = singleton.Singleton()

    def return_dep_list(self):
        return list(self.dependencies.keys())



