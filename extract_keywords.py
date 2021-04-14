from rake_mecab import Rake
import logging
import argparse

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, default="""
    AIチャットボット「りんな」などを手がけるrinna（リンナ）は4月7日、日本語に特化したGPT-2の大規模言語モデルを構築し、GitHubおよびNLPモデルライブラリー「HuggingFace」において、トレーニングコードと言語モデルをオープンソースソフトウェアとして公開した。
また今回公開したモデルは、GPT2-mediumと定義される中規模サイズのものという。今後、パフォーマンスとコストのトレードオフに基づいてユーザーおよび研究者が最善の選択を行えるよう、異なるサイズのモデルも公開する予定。異なるデータでトレーニングした新しいモデルの公開も計画している。
rinnaの研究チームが開発している大規模な言語モデルは、すでに同社プロダクトに広く使用されているという。同社は今後も、異なるテキストスタイルや異なるデータ量を含む、より高精度でより大規模な言語モデルの研究開発を続け、AIチャットボットの能力を高めるとしている。また、日本語の研究コミュニティのために、これらのモデルのオープンソース化を行う。
    """)
    parser.add_argument('--pos', type=str, default="名詞", help="POS tags should split by `,`")
    args = parser.parse_args()

    # Initialize RAKE
    rk = Rake(
        stopwords=[], # <- You can add additional stopwords
        slothlib_stopwords=True, # If True, slothlib_stopwords are automatically added
        punctuations=None, # By default, string.punctuation + "。、"
        mecabtagger_path='-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd', # mecab tagger path
        pos_list=args.pos.split(','),
        # RAKE parameter
        max_length=100000,
        min_length=1,
    )

    # If you have a string of text/documents, this can be used
    rk.extract_keywords_from_text(text=args.text)

    # get ordered phrases
    keywords = rk.get_ranked_phrases()
    for idx, keyword in enumerate(keywords):
        print("{0}) {1}".format(idx+1, keyword))

    # get ordered phrases with scores
    # print(rk.get_ranked_phrases_with_scores())


if __name__ == '__main__':
    main()
