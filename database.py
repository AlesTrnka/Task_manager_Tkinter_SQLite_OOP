import sqlite3


class TaskDtb():
    """
    Práce s databází SQLite pro správu dat úkolů.
    """
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id_úkolu INTEGER PRIMARY KEY AUTOINCREMENT,
                datum DATE,
                název_úkolu TEXT,
                podrobnosti TEXT
                )""")

    def save_task(self, task):
        task_atributes = (task.date, task.subject, task.details)
        self.c.execute("""INSERT OR IGNORE INTO tasks (
                'datum', 'název_úkolu', 'podrobnosti')
                VALUES(?,?,?)""", task_atributes)
        self.conn.commit()

    def view_tasks(self):
        self.c.execute("SELECT id_úkolu, datum, název_úkolu, podrobnosti FROM tasks")
        tasks = self.c.fetchall()
        return tasks

    def update_task(self, values, old_data):
        data = (values[0], values[1], values[2], old_data[0], old_data[1])
        self.c.execute("UPDATE tasks SET datum=?, název_úkolu=?, podrobnosti=? WHERE datum=? AND název_úkolu=?", data)
        self.conn.commit()

    def delete_task(self, values):
        self.c.execute("DELETE from tasks WHERE datum=? AND název_úkolu=?", (values))
        self.conn.commit()
