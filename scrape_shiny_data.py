import sqlite3
import shutil
import os

DATABASE_PATH = ""
users = ["user1", "user2"]


def scrape_databases(users):
        shutil.rmtree(DATABASE_PATH)
        os.mkdir(DATABASE_PATH)
        for user in users:
                shiny_dir = f"/home/{user}/ShinyApps/"
                apps = [folder for folder in os.listdir(shiny_dir) if folder != "log"]
                for app in apps:
                        db_path = f"{os.path.join(shiny_dir, app)}/logs/shinylogs.sqlite"
                        if os.path.exists(db_path):
                                shutil.copy(db_path, f"{DATABASE_PATH}{user}_{app}.sqlite")


def combine_databases():
        dbs = os.listdir(DATABASE_PATH)
        db0 = dbs[0]
        shutil.move(f"{DATABASE_PATH}{db0}", f"{DATABASE_PATH}shiny_database.sqlite")
        if len(dbs) > 1:
                for db in dbs[1:]:
                        con = sqlite3.connect(f"{DATABASE_PATH}shiny_database.sqlite")
                        con.execute("ATTACH '" + f"{DATABASE_PATH}{db}" +  "' as dba")
                        con.execute("BEGIN")
                        for row in con.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
                                combine = "INSERT OR IGNORE INTO "+ row[1] + " SELECT * FROM dba." + row[1]
                                con.execute(combine)
                        con.commit()
                        con.execute("detach database dba")
                        os.remove(f"{DATABASE_PATH}{db}")


if __name__ == "__main__":
	scrape_databases(users)
	combine_databases()