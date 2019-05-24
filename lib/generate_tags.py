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
from unidecode import unidecode

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

query = 'SELECT * FROM c_items WHERE summary IS NULL'
articles = pd.read_sql_query(query, engine)

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

articles["description"] = articles["s_description"]
articles = articles.drop(["s_title", "s_description"], axis=1)
articles.rename(columns={"i_category":"category"}, inplace=True)


def summarize_description(row):
    ts = TextSummarizer()
    ts.input_text(row['description'])
    words = ts.tokenize_sentence()
    freqTable = ts.cal_freq(words)
    sentenceValue = ts.compute_sentence(freqTable)
    # avg = ts.sumAvg(sentenceValue)
    summary = ts.print_summary(sentenceValue, 5)
    analytics_pattern = re.compile("\(.+}\);")
    summary = analytics_pattern.sub("", summary)
    rows = [
        summary,
        row['id']
        ]
    exec_text = 'UPDATE c_items SET summary = %s WHERE id = %s'
    cursor.execute(exec_text, rows)
    db.commit()

print("Generating summary...")
print(articles.head())
articles[["id", "description"]].apply(summarize_description, axis=1)
# input("Updated")
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

print("Getting updated data...")
query = 'SELECT * FROM c_items WHERE s_tags IS NULL AND summary <> ""'
articles = pd.read_sql_query(query, engine)


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


articles['text'] = articles['summary'].apply(clean_text)
articles['text'] = articles['text'].apply(remove_less_than_3words)
# articles['description'] = articles['description'].str.replace("\d+", "")
# articles['description'] = articles['description'].str.replace("\n", "")

print("Vectorizing...")
vectorizer = TfidfVectorizer(stop_words=stopWords)

# vectorizer.vocabulary_

def update_tags(row):
    cursor = db.cursor()
    vector = vectorizer.fit_transform([row["s_title"]+" "+row['text']])
    freqs = zip(vectorizer.get_feature_names(), vector.sum(axis=0).tolist()[0])
    sort_result = sorted(freqs, key=lambda x: -x[1])
    tags = list()
    for tag in sort_result[:5]:
        tags.append(tag[0])

    if row['source'] == "youtube":
        rows = [str(",".join(tags))+",humour,"+row['country'], row['id']]
    else:
        rows = [str(",".join(tags)+","+row['country']), row['id']]
    exec_text = 'UPDATE c_items SET s_tags = %s WHERE id = %s'
    cursor.execute(exec_text, rows)
    db.commit()

try:
    vector = vectorizer.fit_transform([articles.iloc[0].text])
    print("Updating tags...")
    articles.apply(update_tags, axis=1)
except IndexError:
    pass

# input("Update tag")

# Update s_description with tag url
query = 'SELECT id, s_description, s_title, s_url, s_tags, summary, source, image FROM c_items WHERE is_tagged = 0'
df = pd.read_sql_query(query, engine)

print("Check summary and tags")

def update_description_with_tags_url(row):
    if args.env == "dev":
        tags_endpoint = config.dev_url
        auth_key = config.dev_key
    else:
        tags_endpoint = config.prod_url
        auth_key = config.prod_key

    tags_dic, tags_list = post.get_wordpress_tags(tags_endpoint)
    cursor = db.cursor()
    tags_id = list()

    try:
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
            #pattern = re.compile(" "+tag+"[\s\.,;]", re.IGNORECASE)
            pattern = re.compile(r"\b%s\b" % tag, re.IGNORECASE)
            analytics_pattern = re.compile("\(.+}\);")
            row['s_description'] = pattern.sub(tag_url, row['s_description'])
            row['s_description'] = analytics_pattern.sub("", row['s_description'])
            row['summary'] = pattern.sub(" "+tag_url+" ", row['summary'])
            row['summary'] = analytics_pattern.sub("", row['summary'])

        if row['source'] != "youtube":
            print("Updating summary with referer url and image...")

            print(row['summary'], type(row['summary']))
            print(row['source'])
            # input("First state")
            clean_title_slug = re.sub('[^a-zA-Z0-9À-ÿ- \n\.]', ' ', row['s_title'])
            referer_url = "\n\n<p><a href='"+row['s_url']+"' title='"+clean_title_slug+"' target='_blank' rel='nofollow'>Lire l'article en entier sur "+row['source']+"</a></p>"
            image_html = "<p><img src='"+row['image']+"' alt='"\
                            + clean_title_slug + "'></p>\n"

            row['summary'] = image_html+row['summary']+referer_url
        
        print(row['summary'])
        # input('row summary')

        rows = [
            row['summary'],
            '1',
            ",".join(map(str, set(tags_id))),
            '1',
            row['id']
            ]
        exec_text = 'UPDATE c_items SET summary = %s, is_tagged = %s, \
            s_tags_id = %s, is_ready = %s WHERE id = %s'
        cursor.execute(exec_text, rows)
        db.commit()
        print("Stored {}".format(row['id']))
        # input()
    except AttributeError as e:
        print(e)
        pass

# print(post.get_wordpress_tags("https://koravox.com/wp-json/wp/v2/tags"))
print("Updating and summarizing...")
df.apply(update_description_with_tags_url, axis=1)
#update_tags(articles.iloc[0])
