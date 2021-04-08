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
        ans = cursor.execute("SELECT * FROM votes WHERE theme = ? and class = -1 order by RANDOM() LIMIT 1;", (theme,)).fetchall()
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

