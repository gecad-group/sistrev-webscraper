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
        Removes duplicates, entries without title and entries without abstract
        :returns tuple: (number of duplicates, number of entries without title, number of entries without abstract)
        """
        df = pd.DataFrame(self.in_entries)

        data_size = df.shape[0]

        # Removing duplicates
        # (An entry is considered a duplicate if the title, type (Journal, Article, etc...) and abstract are the same.
        # We keep the last entry in the dataframe because that one is usually the most recent, in case a correction was
        # issued to an existing article
        clean_df = df.drop_duplicates(subset=['title', 'type_of_reference', 'abstract'], keep='last')

        n_duplicated = df.shape[0] - clean_df.shape[0]

        # Removing no title
        df = clean_df
        clean_df = df.dropna(subset=['title'])

        n_no_title = df.shape[0] - clean_df.shape[0]

        # Removing no abstract
        df = clean_df
        clean_df = df.dropna(subset=['abstract'])

        n_no_abstract = df.shape[0] - clean_df.shape[0]

        # Removing no DOI entries
        # If an entry does not have a Digital Object Identifier, it is removed as we cannot retrieve the PDF
        #  and the article itself probably isn't very relevant
        df = clean_df
        clean_df = df.dropna(subset=['doi'])

        n_no_doi = df.shape[0] - clean_df.shape[0]

        # store the clean data to out_entries, so we can export later
        self.out_entries = clean_df.to_dict("records")

        # remove keys when value is NaN
        self.out_entries = [{k: v for k, v in x.items() if v == v} for x in self.out_entries]

        # print(clean_df.shape[0])

        return n_duplicated, n_no_title, n_no_abstract, n_no_doi

    def export_data(self, path: str = ""):
        with open(path + '/out.ris', 'w', encoding='utf-8') as outfile:
            rispy.dump(self.out_entries, outfile)

if __name__ == '__main__':
    cleaner = DataCleaner()
    cleaner.add_file('testdata/artf-intl-wos.ris')
    print(cleaner.count_in_entries())
    print(cleaner.clean_entries())
    print(cleaner.count_out_entries())
    # cleaner.export_data()
