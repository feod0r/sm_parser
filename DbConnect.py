import sqlite3
import time
import pymysql


class DbConnect:
    def __init__(self):
        self.path = '../data/classes.db'
        # self.database = sqlite3.connect(self.path, timeout=10)
        self.database = pymysql.connect(host="192.168.1.6", user="romecraft", password="osUUfd7pk1uGjccL", database="mirea", port=3306)
        cursor = self.database.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS `votes` ("
                       "`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                       "`class` int NOT NULL DEFAULT '-1',"
                       "`theme` text NOT NULL,"
                       "`query` text NOT NULL,"
                       "`text` text NOT NULL,"
                       "`link` text NOT NULL)")
        # cursor.execute(
        #     "CREATE TABLE IF NOT EXISTS `votes` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, "
        #     "`class` INT NOT NULL DEFAULT '-1' , "
        #     "`theme` TEXT NOT NULL , "
        #     "`query` TEXT NOT NULL , "
        #     "`text` TEXT NOT NULL, "
        #     "`link` text NOT "
        #     "NULL);") #sqlite
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `paragraph` ( "
            "`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT, "
            "`link` TEXT NOT NULL , "
            "`caption` TEXT DEFAULT NULL , "
            "`text` TEXT NOT NULL , "
            "`theme` TEXT NOT NULL , "
            "`date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `links` ( "
            "`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT, "
            "`link` TEXT NOT NULL , "
            "`caption` TEXT DEFAULT NULL, "
            "`theme` TEXT NOT NULL , "
            "`date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        self.database.commit()
        # cursor.close()
        # database.close()

    def insert(self, theme, query, text, link):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        cursor.execute(
            f"INSERT INTO `votes` (`id`, `class`, `theme`, `query`, `text`, `link`) VALUES (NULL, '-1', '{theme}',"
            f" '{query}', '{text[:500]}', '{link}');")
        self.database.commit()
        # cursor.close()
        # database.close()

    def show_unclassified(self, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute(f"SELECT * FROM votes WHERE theme = '{theme}' and class = -1;")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def take(self, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute(f"SELECT * FROM votes WHERE theme = '{theme}' and class = -1 order by RANDOM() LIMIT 1;")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def show_classified(self, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute(f"SELECT * FROM votes WHERE theme = '{theme}' and class != -1;")

        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def correct_class(self, id_corrected, corrected):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        id_corrected = int(id_corrected)
        corrected = int(corrected)
        cursor.execute(f"UPDATE `votes` SET `class` = {corrected} WHERE `id` = {id_corrected}")
        self.database.commit()
        # cursor.close()
        # database.close()

    def show(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute("SELECT * FROM votes")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def insert_paragraph(self, link, caption, text, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        query = f"SELECT * FROM paragraph WHERE `link` = '{link}' and `text` = '{text}' and `theme` = '{theme}'"

        result = {}
        if cursor.execute(query, (link, text, theme)) == 0:
            query = "INSERT INTO `paragraph` (`id`, `link`, `caption`, `text`, `theme`, `date`) VALUES (NULL, " \
                    f"'{link}', '{caption}', '{text}', '{theme}', CURRENT_TIMESTAMP);"

            cursor.execute(query)

            # если надо сделать подготовку к выборке, иначе закомментировать
            self.insert(theme, 'web page', text, link)

            result = {
                'text': text,
                'se': 'w',
                'wallUrl': link,
                'query': theme,
                'date': time.time(),
                'id': link,
            }
        else:
            result = False
        #             print(len(ans))
        self.database.commit()
        # cursor.close()
        # database.close()
        return result

    def show_paragraph(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute("SELECT * FROM paragraph")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def insert_links(self, link, caption, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        query = f"SELECT * FROM links WHERE `link` = '{link}' and `caption` = '{caption}' and `theme` = '{theme}'"

        if cursor.execute(query) == 0:
            query = "INSERT INTO `links` (`id`, `link`, `caption`, `theme`, `date`) VALUES (NULL, " \
                    f"'{link}', '{caption}', '{theme}', CURRENT_TIMESTAMP);"

            cursor.execute(query)
        else:
            pass
        #             print(len(ans))
        self.database.commit()
        # cursor.close()
        # database.close()

    def show_all_links(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute("SELECT * FROM links")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def show_links(self, theme):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute(f"SELECT * FROM links where `theme` = {theme}")
        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def show_themes_links(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        print(cursor.execute("SELECT theme FROM links GROUP BY theme"))#.fetchall()

        self.database.commit()
        # cursor.close()
        # database.close()
        return cursor.fetchall()

    def _drop_links(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute("DROP TABLE links")
        ans = cursor.execute(
            "CREATE TABLE IF NOT EXISTS `links` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT NOT NULL, `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        print('dropped table links', ans)
        self.database.commit()
        # cursor.close()
        # database.close()
        # return

    def _drop_paragraph(self):
        # database = sqlite3.connect(self.path)
        cursor = self.database.cursor()
        ans = cursor.execute("DROP TABLE paragraph")
        ans = cursor.execute(
            "CREATE TABLE IF NOT EXISTS `paragraph` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT NOT NULL, `text` TEXT NOT NULL , `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        self.database.commit()
        print('dropped table paragraph', ans)
        # cursor.close()
        # database.close()
        # return ans

    def __del__(self):
        self.database.close()
