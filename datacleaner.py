import os.path

import rispy
import pandas as pd


class DataCleaner:
    """
    Cleans the data from a ris file.
    Removes duplicate entries, entries without title and entries without abstract
    """

    def __init__(self):
        # entries to be cleaned
        self.in_entries: list[dict] = []

        # output entries
        self.out_entries: list[dict] = []

    def count_in_entries(self) -> int:
        """Returns the total number of input entries"""

        return len(self.in_entries)

    def count_out_entries(self) -> int:
        """Returns the total number of output entries"""

        return len(self.out_entries)

    def add_file(self, filepath: str) -> None:
        """Adds the entries from a file to self.in_entries"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.in_entries = self.in_entries + rispy.load(f, encoding='utf-8')

    def clean_entries(self) -> tuple[int, int, int, int]:
        """
        Removes duplicates, entries without title, entries without abstract and entries without doi
        :returns tuple: (number of duplicates, number of entries without title, number of entries without abstract, number of entries without doi)
        """
        df = pd.DataFrame(self.in_entries)

        data_size = df.shape[0]
        clean_df = df

        # Removing no DOI entries
        # If an entry does not have a Digital Object Identifier, it is removed as we cannot retrieve the PDF
        #  and the article itself probably isn't very relevant
        # We remove these first, because it's the method that eliminates the most articles
        clean_df, n_no_doi = self.clean_no_doi(clean_df)

        # Removing no title
        clean_df, n_no_title = self.clean_no_title(clean_df)

        # Removing no abstract
        clean_df, n_no_abstract = self.clean_no_abst(clean_df)

        # Removing duplicates.
        # Duplicates are removed last, as the other method eliminate the articles that are "bad data" first
        clean_df, n_duplicated = self.clean_duplicate(clean_df)

        # store the clean data to out_entries, so we can export later
        self.out_entries = clean_df.to_dict("records")

        # remove keys when value is NaN
        self.out_entries = [{k: v for k, v in x.items() if v == v} for x in self.out_entries]

        # print(clean_df.shape[0])

        return n_duplicated, n_no_title, n_no_abstract, n_no_doi

    def clean_no_doi(self, clean_df):
        df = clean_df
        clean_df = df.dropna(subset=['doi'])
        n_no_doi = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_doi

    def clean_no_abst(self, clean_df):
        df = clean_df
        clean_df = df.dropna(subset=['abstract'])
        n_no_abstract = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_abstract

    def clean_no_title(self, clean_df):
        df = clean_df
        clean_df = df.dropna(subset=['title'])
        n_no_title = df.shape[0] - clean_df.shape[0]
        return clean_df, n_no_title

    def clean_duplicate(self, df):
        # Removing duplicates (An entry is considered a duplicate if the title, type (Journal, Article, etc...) and
        # abstract are the same. We keep the first entry in the dataframe because that one is usually the most
        # relevant, per the Web Of Science criteria.
        clean_df = df.drop_duplicates(subset=['title', 'type_of_reference'], keep='first')
        n_duplicated = df.shape[0] - clean_df.shape[0]
        return clean_df, n_duplicated

    def export_data(self, path: str = ""):
        os.makedirs(os.path.abspath(path), exist_ok=True)
        with open(path + '/out.ris', 'w', encoding='utf-8') as outfile:
            rispy.dump(self.out_entries, outfile)

if __name__ == '__main__':
    cleaner = DataCleaner()
    #cleaner.add_file('testdata/artf-intl-wos.ris')

    print("Path of the files to import (Press ENTER with empty input to terminate).")
    f = input(": ")
    while (len(f) > 0):
        cleaner.add_file(os.path.abspath(f))
        f = input(": ")

    print(f'Total number of articles imported: {cleaner.count_in_entries()}')

    n_dup, n_no_title, n_no_abst, n_no_doi = cleaner.clean_entries()
    clean = cleaner.count_out_entries()

    print(f'Number of duplicated entries: {n_dup}')
    print(f'Number of entries without title: {n_no_title}')
    print(f'Number of entries without abstract: {n_no_abst}')
    print(f'Number of entries without doi: {n_no_doi}')
    print(f'Number of entries after cleanup: {clean}')

    cleaner.export_data("export")
