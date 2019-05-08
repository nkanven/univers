import re
import MySQLdb
import sqlalchemy
import pandas as pd
import post
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import config
import argparse
from text_summarizer import TextSummarizer

parser = argparse.ArgumentParser(
    description="Tag generator parameters for Univers")

parser.add_argument(
    "--env",
    dest="env",
    type=str,
    default="dev",
    help="Define the environment for the execution")

args = parser.parse_args()

#MySQL params init
db = MySQLdb.connect(
    config.dbhost,
    config.dbuser,
    config.dbpassword,
    config.dbname)

db.set_character_set('utf8')
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

#df = pd.read_csv("E:/Projects/Univers/extra/articles.csv", encoding="utf-8")
print("Launching sqlalchemy")
engine = sqlalchemy.create_engine("mysql+pymysql://"+config.dbuser+":"+config.dbpassword+"@"+config.dbhost+":3306/"+config.dbname)

query = 'SELECT * FROM c_items WHERE s_tags IS NULL'
df = pd.read_sql_query(query, engine)

articles = df.copy()
articles = articles.drop(
    [
        "s_id",
        "s_author",
        "s_url",
        "s_tags",
        "s_tags_id",
        "is_tagged",
        "is_ready",
        "is_posted",
        "d_date"
    ], axis=1)

articles["description"] = articles["s_title"].astype(str)+" "+articles["s_description"]
articles = articles.drop(["s_title", "s_description"], axis=1)
articles.rename(columns={"i_category":"category"}, inplace=True)

#Preprocessing

#Build stopwords list
print("Removing stopwords")
stop_words = [sw.replace("\n", "") for sw in open(config.stopwords_file_path, encoding="utf-8")]
sw = stop_words
stopWords_fr = set(stopwords.words('french'))
stopWords_en = set(stopwords.words('english'))
stop_words.extend(stopWords_fr)
stop_words.extend(stopWords_en)
stopWords = set(stop_words)
stopWords.remove("")


def remove_less_than_3words(row):
    n_text = ""
    spl_text = row.split(" ")
    for text in spl_text:
        if len(text) > 1:
            n_text += text+" "
    return n_text

"""Remove french caracters
def remove_french_caracters(row):
    text = re.sub('\W+',' ', row['text'])
    return unidecode(text)"""


def clean_text(row):
    #remove number
    text = re.sub('\d+', ' ', row)
    #remove backslashed
    text = re.sub('\n', ' ', text)
    #remove google analytics code
    text = re.sub('\(.+{}\)', ' ', text)
    #remove special caracters
    text = re.sub('[^a-zA-Z0-9À-ÿ- \n\.]', ' ', text)
    return text


articles['text'] = articles['description'].apply(clean_text)
articles['text'] = articles['text'].apply(remove_less_than_3words)
# articles['description'] = articles['description'].str.replace("\d+", "")
# articles['description'] = articles['description'].str.replace("\n", "")

print("Vectorizing...")
vectorizer = TfidfVectorizer(stop_words=stopWords)

# vectorizer.vocabulary_

def update_tags(row):
    cursor = db.cursor()
    vector = vectorizer.fit_transform([row['text']])
    freqs = zip(vectorizer.get_feature_names(), vector.sum(axis=0).tolist()[0])
    sort_result = sorted(freqs, key=lambda x: -x[1])
    tags = list()
    for tag in sort_result[:5]:
        tags.append(tag[0])
    # print(row['text'])
    # print(",".join(tags))
    if row['source'] == "youtube":
        rows = [str(",".join(tags))+",humour", row['id']]
    else:
        rows = [str(",".join(tags)), row['id']]
    exec_text = 'UPDATE c_items SET s_tags = %s WHERE id = %s'
    cursor.execute(exec_text, rows)
    db.commit()

try:
    vector = vectorizer.fit_transform([articles.iloc[0].text])
    print("Updating tags...")
    articles.apply(update_tags, axis=1)
except IndexError:
    pass


# Update s_description with tag url
query = 'SELECT id, s_description, s_title, s_url, s_tags, summary, source FROM c_items WHERE is_tagged = 0'
df = pd.read_sql_query(query, engine)


def update_description_with_tags_url(row):
    if args.env == "dev":
        tags_endpoint = config.dev_tags_endpoint
        auth_key = config.dev_post_key
    else:
        tags_endpoint = config.prod_tags_endpoint
        auth_key = config.prod_post_key

    tags_dic, tags_list = post.get_wordpress_tags(tags_endpoint)
    cursor = db.cursor()
    tags_id = list()
    for tag in row['s_tags'].split(","):
        if tag not in tags_list:
            t_id = post.create_tag(tag, tags_endpoint, auth_key)

            if t_id is None:
                continue
            
            tags_id.append(t_id)
        else:
            tags_id.append(tags_dic[tag])

        tag_url = "<a href='/tag/{}' title='Recherche de {}'>{}</a>"\
            .format(tag, tag, tag)
        pattern = re.compile(" "+tag+"[\s\.,;]", re.IGNORECASE)
        analytics_pattern = re.compile("\(.+}\);")
        row['s_description'] = pattern.sub(" "+tag_url+" ", row['s_description'])
        row['s_description'] = analytics_pattern.sub("", row['s_description'])

        print(row['summary'], type(row['summary']))
        print(row['source'])

        if row['source'] != "youtube":
            if row['summary'] is None:
                print("Summarizing description...")
                f_description = row['s_description'].split("</p>")
                image_html = f_description[0]+"</p>\n"
                referer_url = "\n\n<p><a href='"+row['s_url']+"' title='"+row['s_title']+"' target='_blank' rel='nofollow'>Lire l'article en entier en cliquant ici</a></p>"
                
                print(referer_url)
                ts = TextSummarizer()
                ts.input_text("</p>\n".join(f_description[1:]))
                words = ts.tokenize_sentence()
                freqTable = ts.cal_freq(words)
                sentenceValue = ts.compute_sentence(freqTable)
                avg = ts.sumAvg(sentenceValue)
                summary = ts.print_summary(sentenceValue, avg)
                analytics_pattern = re.compile("\(.+}\);")
                summary = analytics_pattern.sub("", summary)
                summary = pattern.sub(" "+tag_url+" ", summary)
                summary = analytics_pattern.sub("",summary)
                row['summary'] = image_html+summary+referer_url

    rows = [
        row['s_description'],
        row['summary'],
        '1',
        ",".join(map(str, set(tags_id))),
        '1',
        row['id']
        ]
    exec_text = 'UPDATE c_items SET s_description = %s, summary = %s, is_tagged = %s, \
        s_tags_id = %s, is_ready = %s WHERE id = %s'
    cursor.execute(exec_text, rows)
    db.commit()


# print(post.get_wordpress_tags("https://koravox.com/wp-json/wp/v2/tags"))
print("Updating and summarizing...")
df.apply(update_description_with_tags_url, axis=1)
#update_tags(articles.iloc[0])
