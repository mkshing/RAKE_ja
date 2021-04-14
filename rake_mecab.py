import string
from collections import Counter, defaultdict
from itertools import chain, groupby, product
import re
from enum import Enum
import urllib
import urllib.request
import MeCab

class Metric(Enum):
    """Different metrics that can be used for ranking."""

    DEGREE_TO_FREQUENCY_RATIO = 0  # Uses d(w)/f(w) as the metric
    WORD_DEGREE = 1  # Uses d(w) alone as the metric
    WORD_FREQUENCY = 2  # Uses f(w) alone as the metric


class Tokenizer:

    def __init__(
        self,
        mecabtagger_path,
        pos_list
    ):
        self.pos_list = pos_list
        self.tagger = MeCab.Tagger(mecabtagger_path)
        self.tagger.parse('')
    
    def _tokenize(self, text):
        node = self.tagger.parseToNode(text)
        terms = []
        while node:
            # 単語
            term = node.surface
            # 品詞
            pos = node.feature.split(',')
            # もし品詞が条件と一致してたら
            if pos[0] in self.pos_list:
                terms.append(term)
                
            node = node.next
        return terms
    
    def _text2senteces(self, text):
        # ？　、　。　！
        return filter(lambda w: len(w) > 0, re.split(r'？|。|w|！|\.|（笑）', text))
    
    
class Rake(object):
    """Rapid Automatic Keyword Extraction Algorithm."""

    def __init__(
        self,
        stopwords=None,
        slothlib_stopwords=True,
        punctuations=None,
        ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO,
        max_length=100000,
        min_length=1,
        mecabtagger_path='-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd',
        pos_list=['形容詞', '名詞', '動詞'],
    ):
        """Constructor.
        :param stopwords: List of Words to be ignored for keyword extraction.
        :param punctuations: Punctuations to be ignored for keyword extraction.
        :param max_length: Maximum limit on the number of words in a phrase
                           (Inclusive. Defaults to 100000)
        :param min_length: Minimum limit on the number of words in a phrase
                           (Inclusive. Defaults to 1)
        """
        # By default use degree to frequency ratio as the metric.
        if isinstance(ranking_metric, Metric):
            self.metric = ranking_metric
        else:
            self.metric = Metric.DEGREE_TO_FREQUENCY_RATIO

        if slothlib_stopwords or stopwords is None:
            slothlib_path = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
            slothlib_file = urllib.request.urlopen(slothlib_path)
            slothlib_stopwords = [line.decode("utf-8").strip() for line in slothlib_file]
            slothlib_stopwords = [ss for ss in slothlib_stopwords if not ss==u'']
            self.stopwords = slothlib_stopwords
            
        if isinstance(stopwords, list):
            self.stopwords = self.stopwords + stopwords
            

        self.punctuations = punctuations
        if self.punctuations is None:
            self.punctuations = string.punctuation + "。、"

        # All things which act as sentence breaks during keyword extraction.
        self.to_ignore = set(chain(self.stopwords, self.punctuations))

        # Assign min or max length to the attributes
        self.min_length = min_length
        self.max_length = max_length

        # Stuff to be extracted from the provided text.
        self.frequency_dist = None
        self.degree = None
        self.rank_list = None
        self.ranked_phrases = None
        
        # Set tokenizer
        self.tokenizer = Tokenizer(mecabtagger_path, pos_list)

    def extract_keywords_from_text(self, text):
        """Method to extract keywords from the text provided.
        :param text: Text to extract keywords from, provided as a string.
        """
        # sentences = nltk.tokenize.sent_tokenize(text)
        sentences = self.tokenizer._text2senteces(text)
        self.extract_keywords_from_sentences(sentences)

    def extract_keywords_from_sentences(self, sentences):
        """Method to extract keywords from the list of sentences provided.
        :param sentences: Text to extraxt keywords from, provided as a list
                          of strings, where each string is a sentence.
        """
        phrase_list = self._generate_phrases(sentences)
        self._build_frequency_dist(phrase_list)
        self._build_word_co_occurance_graph(phrase_list)
        self._build_ranklist(phrase_list)

    def get_ranked_phrases(self):
        """Method to fetch ranked keyword strings.
        :return: List of strings where each string represents an extracted
                 keyword string.
        """
        return self.ranked_phrases

    def get_ranked_phrases_with_scores(self):
        """Method to fetch ranked keyword strings along with their scores.
        :return: List of tuples where each tuple is formed of an extracted
                 keyword string and its score. Ex: (5.68, 'Four Scoures')
        """
        return self.rank_list

    def get_word_frequency_distribution(self):
        """Method to fetch the word frequency distribution in the given text.
        :return: Dictionary (defaultdict) of the format `word -> frequency`.
        """
        return self.frequency_dist

    def get_word_degrees(self):
        """Method to fetch the degree of words in the given text. Degree can be
        defined as sum of co-occurances of the word with other words in the
        given text.
        :return: Dictionary (defaultdict) of the format `word -> degree`.
        """
        return self.degree

    def _build_frequency_dist(self, phrase_list):
        """Builds frequency distribution of the words in the given body of text.
        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        self.frequency_dist = Counter(chain.from_iterable(phrase_list))

    def _build_word_co_occurance_graph(self, phrase_list):
        """Builds the co-occurance graph of words in the given body of text to
        compute degree of each word.
        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        co_occurance_graph = defaultdict(lambda: defaultdict(lambda: 0))
        for phrase in phrase_list:
            # For each phrase in the phrase list, count co-occurances of the
            # word with other words in the phrase.
            #
            # Note: Keep the co-occurances graph as is, to help facilitate its
            # use in other creative ways if required later.
            for (word, coword) in product(phrase, phrase):
                co_occurance_graph[word][coword] += 1
        self.degree = defaultdict(lambda: 0)
        for key in co_occurance_graph:
            self.degree[key] = sum(co_occurance_graph[key].values())

    def _build_ranklist(self, phrase_list):
        """Method to rank each contender phrase using the formula
              phrase_score = sum of scores of words in the phrase.
              word_score = d(w)/f(w) where d is degree and f is frequency.
        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        self.rank_list = []
        for phrase in phrase_list:
            rank = 0.0
            for word in phrase:
                if self.metric == Metric.DEGREE_TO_FREQUENCY_RATIO:
                    rank += 1.0 * self.degree[word] / self.frequency_dist[word]
                elif self.metric == Metric.WORD_DEGREE:
                    rank += 1.0 * self.degree[word]
                else:
                    rank += 1.0 * self.frequency_dist[word]
            self.rank_list.append((rank, " ".join(phrase)))
        self.rank_list.sort(reverse=True)
        self.ranked_phrases = [ph[1] for ph in self.rank_list]

    def _generate_phrases(self, sentences):
        """Method to generate contender phrases given the sentences of the text
        document.
        :param sentences: List of strings where each string represents a
                          sentence which forms the text.
        :return: Set of string tuples where each tuple is a collection
                 of words forming a contender phrase.
        """
        phrase_list = set()
        # Create contender phrases from sentences.
        for sentence in sentences:
            word_list = self.tokenizer._tokenize(sentence)
            # word_list = [word.lower() for word in wordpunct_tokenize(sentence)]
            phrase_list.update(self._get_phrase_list_from_words(word_list))
        return phrase_list

    def _get_phrase_list_from_words(self, word_list):
        """Method to create contender phrases from the list of words that form
        a sentence by dropping stopwords and punctuations and grouping the left
        words into phrases. Only phrases in the given length range (both limits
        inclusive) would be considered to build co-occurrence matrix. Ex:
        Sentence: Red apples, are good in flavour.
        List of words: ['red', 'apples', ",", 'are', 'good', 'in', 'flavour']
        List after dropping punctuations and stopwords.
        List of words: ['red', 'apples', *, *, good, *, 'flavour']
        List of phrases: [('red', 'apples'), ('good',), ('flavour',)]
        List of phrases with a correct length:
        For the range [1, 2]: [('red', 'apples'), ('good',), ('flavour',)]
        For the range [1, 1]: [('good',), ('flavour',)]
        For the range [2, 2]: [('red', 'apples')]
        :param word_list: List of words which form a sentence when joined in
                          the same order.
        :return: List of contender phrases that are formed after dropping
                 stopwords and punctuations.
        """
        groups = groupby(word_list, lambda x: x not in self.to_ignore)
        phrases = [tuple(group[1]) for group in groups if group[0]]
        return list(
            filter(
                lambda x: self.min_length <= len(x) <= self.max_length, phrases
            )
        )