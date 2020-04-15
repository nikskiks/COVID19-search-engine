import json
from pathlib import Path

import pandas as pd
import tqdm
from nltk import sent_tokenize
from nltk.corpus import stopwords

from dataset.util import extract_data_from_dict
from settings import data_root_path

abstract_keys = ('section', 'text')
body_text_keys = ('section', 'text')


class CovidDataLoader():

    @staticmethod
    def load_articles_paths(root_path=data_root_path, file_extension='json'):
        """
        Gets the paths to all files with the given file extension,
        in the given directory(root_path) and all its subdirectories.

        Args:
            root_path: path to directory to get the files from
            file_extension: extension to look for

        Returns:
            list of paths to all articles from the root directory
        """
        article_paths = []
        for path in Path(root_path).rglob('*.%s' % file_extension):
            article_paths.append(str(path))
        return article_paths

    @staticmethod
    def load_data(articles_paths, key='abstract', offset=0, limit=None, keys=abstract_keys, load_sentences=False):
        """
        Given the list of paths to articles json files, returns pandas DataFrame containing the info defined by the keys param.

        e.g. considering the following scheme
            {
            ...
            abstract:
                section: "ABSTRACT", \n
                text: "lorem ipsum..."
            ...
            }
        if key="abstracts" and keys = ["section", "text"], then the method will extract for each abtsract all sections and belonging texts

        Args:
            articles_paths: list of paths to articles to load
            key: defines which part of data to extract from the json-s, e.g. if 'articles' -> extracts articles, if 'body_text' -> extracts body text
            offset: loading start index in the articles_paths list
            limit: number of articles to load
            keys: specifier for the data defined by the key
            load_sentences: if true, it divides the sections further into sentences

        Returns:

        """
        N = len(articles_paths)
        assert offset < N
        last_index = N
        if limit and offset + limit < N:
            last_index = offset + limit

        data_ = []
        for path in tqdm.tqdm(articles_paths[offset:last_index]):
            with open(path, 'r') as f:
                curr_article = json.load(f)
                if key in curr_article:
                    for section in curr_article[key]:
                        curr_part = {'paper_id': curr_article['paper_id']}
                        try:
                            curr_part.update(extract_data_from_dict(section, keys, mandatory_keys=['text']))
                            data_.append(curr_part)
                        except:
                            pass

        if load_sentences:
            return CovidDataLoader.__load_sentences(data_)
        return pd.DataFrame(data_)

    @staticmethod
    def __load_sentences(texts):
        sentences = []
        for text in texts:
            sents = sent_tokenize(text['text'])

            for i in range(len(sents)):
                # TODO: probaj krace rec izbaciti...
                """ls = len(sents[i].split())
                print(sents[i][-1])
                """
                sent = {k: v for k, v in text.items()}
                sent['text'] = sents[i]
                sent['position'] = i
                sentences.append(sent)
        return pd.DataFrame(sentences)


if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))

    body_text_keys = ('section', 'text')
    article_paths = CovidDataLoader.load_articles_paths(data_root_path)
    abstracts = CovidDataLoader.load_data(article_paths, offset=5000, limit=10, load_sentences=True)
    # body_text_sents = CovidDataLoader.load_data(article_paths, key='body_text', keys=body_text_keys, offset=5000,
    #                                            limit=5000, load_sentences=True)