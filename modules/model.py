"""Univers model class to handle CRUD operations."""
import MySQLdb
from _mysql_exceptions import IntegrityError
from lib import config


class models():
    """models with multiple CRUD methods."""

    def __init__(self):
        """Open database connection and params initialization."""
        self.db = MySQLdb.connect(
            config.dbhost,
            config.dbuser,
            config.dbpassword,
            config.dbname)

        self.db.set_character_set('utf8')

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def get_links(self):
        """Return all links available for scraping."""
        sql = "SELECT * FROM links"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        return result
    

    def get_news_links(self):
        """Return all links available for scraping."""
        sql = "SELECT * FROM links WHERE s_type <> 'youtube'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        return result

    def insert_item(self, item, source=None):
        """Insert item into items table.

        Arguments:
            item {list} -- list of item containing table column values
        """

        description = item[3]

        if source == "youtube":
            description = item[5]+"\n"+item[3]
        
        print(source, item[2])
        sql = """INSERT INTO c_items(
            s_id,
            s_title,
            s_description,
            s_author,
            s_url,
            source,
            i_category)
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(
            MySQLdb.escape_string(item[2]).decode("utf-8"),
            MySQLdb.escape_string(item[1]).decode("utf-8"),
            MySQLdb.escape_string(description).decode("utf-8"),
            MySQLdb.escape_string(item[0]).decode("utf-8"),
            MySQLdb.escape_string(item[5]).decode("utf-8"),
            MySQLdb.escape_string(source).decode("utf-8"),
            item[4])
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except IntegrityError:
            pass
    

    def get_items(self):
        # sql = """SELECT * FROM c_items where source = 'youtube'"""
        sql = """SELECT * FROM `c_items` WHERE source <> "youtube" AND is_posted=0 and summary IS NOT NULL"""
        self.cursor.execute(sql)

        return self.cursor.fetchall()


    def update_item(self, item_id):
        rows = ['1', item_id]
        sql = 'UPDATE c_items SET is_posted = %s WHERE id = %s'
        self.cursor.execute(sql, rows)
        self.db.commit()
