import sqlite3


class DbConnect:
    def __init__(self):
        self.path = '../data/classes.db'
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `votes` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `class` INT NOT NULL "
            "DEFAULT '-1' , `theme` TEXT NOT NULL , `query` TEXT NOT NULL , `text` TEXT NOT NULL, `link` text NOT "
            "NULL);")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `paragraph` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT DEFAULT NULL , `text` TEXT NOT NULL , `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS `links` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT DEFAULT NULL, `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        database.commit()
        cursor.close()
        database.close()

    def insert(self, theme, query, text, link):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO `votes` (`id`, `class`, `theme`, `query`, `text`, `link`) VALUES (NULL, '-1', ?, ?, ?, ?);",
            (theme, query, text[:500], link))
        database.commit()
        cursor.close()
        database.close()

    def show_unclassified(self, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM votes WHERE theme = ? and class = -1;", (theme,)).fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def take(self, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM votes WHERE theme = ? and class = -1 order by RANDOM() LIMIT 1;",
                             (theme,)).fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def show_classified(self, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM votes WHERE theme = ? and class != -1;", (theme,)).fetchall()

        database.commit()
        cursor.close()
        database.close()
        return ans

    def correct_class(self, id_corrected, corrected):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        id_corrected = int(id_corrected)
        corrected = int(corrected)
        cursor.execute("UPDATE `votes` SET `class` = ? WHERE `id` = ?", (corrected, id_corrected,))
        database.commit()
        cursor.close()
        database.close()

    def show(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM votes").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def insert_paragraph(self, link, caption, text, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        query = "SELECT * FROM paragraph WHERE `link` = ? and `text` = ? and `theme` = ?"
        ans = cursor.execute(query, (link, text, theme)).fetchall()
        if len(ans) == 0:
            query = "INSERT INTO `paragraph` (`id`, `link`, `caption`, `text`, `theme`, `date`) VALUES (NULL, " \
                    "?, ?, ?, ?, CURRENT_TIMESTAMP);"

            cursor.execute(query, (link, caption, text, theme))

            #если надо сделать подготовку к выборке
            self.insert(theme, 'web page', text, link)
        else:
            pass
        #             print(len(ans))
        database.commit()
        cursor.close()
        database.close()

    def show_paragraph(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM paragraph").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def insert_links(self, link, caption, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        query = "SELECT * FROM links WHERE `link` = ? and `caption` = ? and `theme` = ?"
        ans = cursor.execute(query, (link, caption, theme)).fetchall()
        if len(ans) == 0:
            query = "INSERT INTO `links` (`id`, `link`, `caption`, `theme`, `date`) VALUES (NULL, " \
                    "?, ?, ?, CURRENT_TIMESTAMP);"

            cursor.execute(query, (str(link), str(caption), str(theme)))
        else:
            pass
        #             print(len(ans))
        database.commit()
        cursor.close()
        database.close()

    def show_all_links(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM links").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def show_links(self, theme):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT * FROM links where `theme` = ?", (theme,)).fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def show_themes_links(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("SELECT theme FROM links GROUP BY theme").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans


    def _drop_links(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("DROP TABLE links").fetchall()
        ans = cursor.execute(
            "CREATE TABLE IF NOT EXISTS `links` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT NOT NULL, `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans

    def _drop_paragraph(self):
        database = sqlite3.connect(self.path)
        cursor = database.cursor()
        ans = cursor.execute("DROP TABLE paragraph").fetchall()
        ans = cursor.execute(
            "CREATE TABLE IF NOT EXISTS `paragraph` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `link` TEXT NOT NULL , "
            "`caption` TEXT NOT NULL, `text` TEXT NOT NULL , `theme` TEXT NOT NULL , `"
            "date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)").fetchall()
        database.commit()
        cursor.close()
        database.close()
        return ans
