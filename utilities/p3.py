import singleton
import fitz
from custom_types.Wine import Wine
from custom_types.Flight import Flight
import re


class P3:
    title_pattern = r"(.+),\s(.+)\s\((NV|\d{4})\)"
    owner = 'provi_upload'

    def __init__(self):
        self.flight = None
        self.s = singleton.Singleton()
        self.reset()

    def close_out(self):
        self.flight.pre_flight()
        self.flight.parse_orphans()
        self.s.Save.save_all_wines(self.flight)

    def load(self, file, user_id, filename):
        doc = fitz.open(file)  # open a document
        pages = []
        sections = []
        previous_line = ''
        index = -1

        for page in doc:  # iterate the document pages
            text = page.get_text()  # get plain text
            pages.append(text)  # append decoded text

        for page in pages:
            # Split the text into lines
            lines = page.split('\n')
            line_index = 0
            for line in lines:
                if line == 'Bottles':
                    index += 1  # Increment index for a new section
                    sections.append([])  # Create a new section list
                    title = self.recurse_titles(previous_line, lines, line_index)
                    sections[index].append(title)

                else:
                    if index >= 0:  # Ensure index is valid before appending
                        sections[index].append(previous_line)  # Add line to current section
                line_index += 1
                previous_line = line  # Keep track of the previous line
        self.flight.set_title(filename)
        for section in sections:
            wine = Wine(section, owner=self.owner)
            self.flight.append_wine(wine=wine, owner_id=user_id)
            self.flight.owner_id = user_id

    def recurse_titles(self, title, lines, line_index, line_index_offset=2):
        matches = re.findall(self.title_pattern, title)
        if len(matches) < 1:
            prev_string = lines[line_index - line_index_offset]
            new_title = prev_string + ' ' + title
            return self.recurse_titles(new_title, lines, line_index, line_index_offset + 1)
        else:
            return title

    def reset(self):
        self.flight = Flight(self.owner)
