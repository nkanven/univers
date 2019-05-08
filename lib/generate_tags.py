import re
import MySQLdb
import sqlalchemy
import pandas as pd
import post
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import config


#MySQL params init
db = MySQLdb.connect(config.dbhost, config.dbuser, config.dbpassword, config.dbname)
db.set_character_set('utf8')
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

#df = pd.read_csv("E:/Projects/Univers/extra/articles.csv", encoding="utf-8")
engine = sqlalchemy.create_engine("mysql+pymysql://"+config.dbuser+":"+config.dbpassword+"@"+config.dbhost+":3306/"+config.dbname)


df = pd.read_sql_table("c_items", engine)

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

vectorizer = TfidfVectorizer(stop_words=stopWords)

vector = vectorizer.fit_transform([articles.iloc[0].text])

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


articles.apply(update_tags, axis=1)


# Update s_description with tag url
query = 'SELECT id, s_description, s_tags FROM c_items WHERE s_tags IS NOT NULL AND is_ready = 0 AND source <> "youtube"'
df = pd.read_sql_query(query, engine)


def update_description_with_tags_url(row):
    # tags_dic, tags_list = post.get_wordpress_tags("http://localhost/wordpress/wp-json/wp/v2/tags")
    tags_dic, tags_list = post.get_wordpress_tags("https://koravox.com/wp-json/wp/v2/tags")
    cursor = db.cursor()
    tags_id = list()
    for tag in row['s_tags'].split(","):
        if tag not in tags_list:
            # t_id = post.create_tag(tag, "http://localhost/wordpress/wp-json/wp/v2/tags")
            t_id = post.create_tag(tag, "https://koravox.com/wp-json/wp/v2/tags")

            # print("tag id "+str(t_id))
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
    print(tags_id)
    rows = [row['s_description'], '1', ",".join(map(str, set(tags_id))), '1', row['id']]
    exec_text = 'UPDATE c_items SET s_description = %s, is_tagged = %s, \
        s_tags_id = %s, is_ready = %s WHERE id = %s'
    cursor.execute(exec_text, rows)
    db.commit()


# print(post.get_wordpress_tags("https://koravox.com/wp-json/wp/v2/tags"))
df.apply(update_description_with_tags_url, axis=1)
print(df.head())
#update_tags(articles.iloc[0])
