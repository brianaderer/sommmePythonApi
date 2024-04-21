from py_pdf_parser.loaders import load_file
import re
import singleton


class Parser:
    def __init__(self):
        self.lookup = None
        self.s = None
        self.wine_complete = None
        self.current_terms = None
        self.terms = None
        self.all_wines = None
        self.date_pattern = None
        self.current_wine = None
        self.vintage_pattern = None
        self.provi_pattern = None
        self.bottle_pattern = None
        self.case_pattern = None
        self.wine_pattern = None
        self.unit_pattern = None
        self.reset()

    def reset(self):
        self.unit_pattern = r'^\$(\/bottle|\/case|\/oz)'
        self.wine_pattern = r'[\S]* - [\S]* - [\S]*'
        self.case_pattern = r'\((\d)[a-z]*\)'
        self.bottle_pattern = r'[\d]* [a-zA-Z]* × [\d]*'
        self.provi_pattern = r'provi'
        self.vintage_pattern = r'\((.*?)\)'
        self.current_wine = {'full_title': ''}
        self.date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})'
        self.all_wines = []
        self.terms = ['Producer', 'Region', 'Grape', 'Appellation', 'Size', 'SKU']
        self.current_terms = []
        self.wine_complete = False
        self.s = singleton.Singleton()
        self.lookup = {
            'Class': 'classes',
            'Grape': 'grapes',
            'Appellation': 'appellations',
            'Color': 'colors',
            'cuvee': 'cuvees',
            'Producer': 'producers',
            'Region': 'regions',
            'SKU': 'skus',
            'Size': 'sizes',
            'Type': 'types',
        }
        print('Initialized')

    def load(self, file):
        pdf = load_file(file)
        # visualise(pdf)  # Uncomment to visualize the PDF content
        elements = pdf.elements
        self.parse_data(elements)

    def contains_pattern(self, string, pattern, case_insensitive=True):
        if case_insensitive:
            regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = re.compile(pattern)
        return bool(regex.search(string))

    def sort_terms(self, terms):
        # Create a dictionary that maps term to its index in order_template
        priority = {term: i for i, term in enumerate(self.terms)}

        # Sort the terms based on their index in order_template, terms not in the template will be at the end
        sorted_terms = sorted(terms, key=lambda x: priority.get(x, float('inf')))
        return sorted_terms

    def find_overlap(self, list1, list2):
        overlap = []
        for item1 in list1:
            for item2 in list2:
                if item1 in item2 or item2 in item1:
                    overlap.append(item2)
        return overlap

    def find_cuvee(self):
        parsed_str = self.current_wine['full_title'].replace(self.current_wine['Producer'] + ', ', '')
        regex = re.compile(self.vintage_pattern)
        vintage = regex.search(self.current_wine['full_title'])
        if vintage:
            self.current_wine['vintage'] = vintage.group().replace('(', '').replace(')', '')
            self.current_wine['cuvee'] = parsed_str.replace(' ' + vintage.group(), '')
        else:
            self.current_wine['cuvee'] = parsed_str

    def parse(self, string):
        return string.split(', ')

    def parse_size(self, string):
        return string.split(' × ')

    def parse_wine(self, wine):
        parsed_wine = {}
        for key in wine:
            if key in self.lookup:
                if self.lookup[key] == 'regions':
                    list = self.parse(wine[key])
                    parsed_wine['countries'] = list[1]
                    parsed_wine['regions'] = list[0]
                elif self.lookup[key] == 'grapes':
                    parsed_wine['grapes'] = self.parse(wine[key])
                elif self.lookup[key] == 'sizes':
                    parsed_wine['sizes'] = self.parse_size(wine[key])[0]
                    parsed_wine['cases'] = self.parse_size(wine[key])[1]
                else:
                    parsed_wine[self.lookup[key]] = wine[key]
            else:
                parsed_wine[key] = wine[key]
        return parsed_wine

    def parse_data(self, elements):
        for element in elements:
            text = element.text()
            parse_list = (text.split('\n'))
            if (not self.contains_pattern(parse_list[0], self.unit_pattern)
                and not self.contains_pattern(parse_list[0], self.case_pattern)) \
                    and not self.contains_pattern(parse_list[0], self.provi_pattern) \
                    and not self.contains_pattern(parse_list[0], self.date_pattern) \
                    and not self.contains_pattern(parse_list[0], self.bottle_pattern):
                if not len(parse_list) > 1:
                    continue
                if not self.contains_pattern(parse_list[0], self.wine_pattern):
                    if parse_list[0] == 'Bottles':
                        continue
                    self.current_wine['full_title'] = parse_list[0]
                    self.current_terms = self.find_overlap(parse_list, self.terms)
                else:
                    index = 1
                    type_list = parse_list[0].split(' - ')
                    self.current_wine['Class'] = type_list[0]
                    self.current_wine['Type'] = type_list[1]
                    self.current_wine['Color'] = type_list[2]
                    for term in self.sort_terms(self.current_terms):
                        self.current_wine[term] = parse_list[index]
                        index += 1
                    self.current_terms = []
                    self.wine_complete = True
                if self.wine_complete:
                    self.find_cuvee()
                    self.all_wines.append(self.current_wine)
                    self.current_wine = {'full_title': ''}
                    self.wine_complete = False

        self.s.Save.save_all_wines(self.all_wines)
