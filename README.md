# rake_mecab
RAKE (Rapid Automatic Keyword Extraction) for Japanese text using Mecab.

RAKE is one of statistical method to extract keywords from sentences. 

✨You can set POS depending on your work

✨Without setting stopwords, automatically set default Japanese stopwords! 

## Installation
#### Install Mecab
This [Qita](https://qiita.com/sudo5in5k/items/f89d9dc1bec1ed221ede) explains well. 

#### Install RAKE_ja
```
git clone https://github.com/mkshing/RAKE_ja.git
cd RAKE_ja
```

## Usage
```
from rake_mecab import Rake

# Initialize RAKE
rk = Rake(
    stopwords=[], # <- You can add additional stopwords
    slothlib_stopwords=True, # If True, slothlib_stopwords are automatically added
    punctuations=None, # By default, string.punctuation + "。、"
    mecabtagger_path='-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd', # mecab tagger path 
    pos_list=['名詞', '動詞', '形容詞'],
    # RAKE parameter
    max_length=100000,
    min_length=1,
)

# If you have a list of sentence, this can be used
rk.extract_keywords_from_sentences(sentences=sentences_list)

# If you have a string of text/documents, this can be used
rk.extract_keywords_from_text(text=text)

# get ordered phrases 
rk.get_ranked_phrases()

# get ordered phrases with scores
rk.get_ranked_phrases_with_scores()

```

## Demo
```
> python extract_keywords.py
1) GPT -2 大規模 言語モデル 構築 GitHub および NLP モデル ライブラリー HuggingFace トレーニング コード 言語モデル オープンソースソフトウェア 公開
2) 同社 今後 テキスト スタイル データ 量 精度 大規模 言語モデル 研究開発 AI チャットボット 能力
3) rinna 研究 チーム 開発 大規模 言語モデル 同社 プロダクト 使用
4) AI チャットボット りんな rinna リンナ 4月7日 日本語 特
5) 今後 パフォーマンス コスト トレードオフ ユーザー 研究者 最善 選択
6) 公開 モデル GP T2 medium 定義 中規模 サイズ
7) データ トレーニング モデル 公開 計画
8) サイズ モデル 公開 予定
9) 日本語 研究 コミュニティ
10) モデル オープンソース
```
## Reference
- This is a python implementation of the algorithm as mentioned in paper [Automatic keyword extraction from individual documents by Stuart Rose, Dave Engel, Nick Cramer and Wendy Cowley](https://www.researchgate.net/publication/227988510_Automatic_Keyword_Extraction_from_Individual_Documents)
- [rake-nltk](https://github.com/csurfer/rake-nltk)

## Advance
You can feel free to fork this repo and changes the code for your work! 