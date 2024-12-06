import requests
from bs4 import BeautifulSoup
import sqlite3
from functools import wraps

urls = {"areas of study": "https://uust.ru/admission/bachelor-and-specialist/adm-plan/2024/",
        "prices_of_paid": "https://uust.ru/admission/bachelor-and-specialist/tuition-fees/2024/",
        "score_last_years": "https://uust.ru/admission/bachelor-and-specialist/passing-scores/2024/"}


def get_table(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all("table")
    all_tables = []
    for table in tables:
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            rows.append(cells)
        all_tables.append(rows)
    return all_tables


class ManagerSQL:
    def __init__(self, name):
        self.conn = None
        self.name = name
        self.is_open = False

    @staticmethod
    def access(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_open:
                return func(self, *args, **kwargs)
            else:
                print("В доступе отказано")
                return None

        return wrapper

    @access
    def scrap(self) -> None:
        cursor = self.conn.cursor()
        for do in urls:
            url = urls[do]
            if do == 'areas of study':
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS aos_person (
                    code TEXT NOT NULL,
                    name TEXT NOT NULL,
                    profile TEXT NOT NULL,
                    facultative TEXT NOT NULL,
                    count_budget INTEGER NOT NULL,
                    count_paid INTEGER NOT NULL
                )
                ''')
                cursor.execute('DELETE FROM aos_person')
                table = get_table(url=url)[0][4:]
                data = list(list())
                for area in table:
                    has_code = (((area[0].split())[0]).split('.'))[0].isdigit()
                    if has_code:
                        code, name = (area[0].split())[0], ' '.join((area[0].split())[1:])
                        profile = area[1]
                        facultative = area[2]
                        count_budget = int(area[3]) if area[3] else 0
                        count_paid = int(area[8]) if area[8] else 0
                    else:
                        code, name = data[-1][0], data[-1][1]
                        profile = area[0]
                        facultative = area[1]
                        count_budget = int(area[2]) if area[2] else 0
                        count_paid = int(area[7]) if area[7] else 0
                    if count_paid != 0 or count_budget != 0:
                        data.append((code, name, profile, facultative, count_budget, count_paid))
                cursor.executemany('''INSERT INTO aos_person (code, name, profile, facultative, count_budget, count_paid) VALUES (?, ?, ?, ?, ?, ?)''', data)
            elif do == "prices_of_paid":
                cursor.execute('''
                                CREATE TABLE IF NOT EXISTS po_paid (
                                    code TEXT NOT NULL,
                                    name TEXT NOT NULL,
                                    profile TEXT NOT NULL,
                                    price INTEGER NOT NULL
                                )
                                ''')
                cursor.execute('DELETE FROM po_paid')
                tables = get_table(url=url)[:2]
                data = list(list())
                for table in tables:
                    for line in table[2:]:
                        if line[3] == "Очная":
                            code, name, profile, price = line[0], line[1], line[2], int(line[4])
                            data.append((code, name, profile, price))
                cursor.executemany('''INSERT INTO po_paid (code, name, profile, price) VALUES (?, ?, ?, ?)''', data)
            elif do == "score_last_years":
                tables = get_table(url=url)[:2]
                cursor.execute(f'''
                               CREATE TABLE IF NOT EXISTS sl_years (
                               code TEXT NOT NULL,
                               name TEXT NOT NULL,
                               average INTEGER NOT NULL
                               )
                               ''')
                cursor.execute('DELETE FROM sl_years')
                data = list(list())
                for table in tables:
                    for line in table[1:]:
                        average = [int(i) for i in line[2:] if i.isdigit()]
                        code, name, average = line[0], line[1], sum(average) // len(average)
                        data.append((code, name, average))
                cursor.executemany('''INSERT INTO sl_years (code, name, average) VALUES (?, ?, ?)''', data)
        self.conn.commit()
        self.close()

    def open(self):
        self.is_open = True
        self.conn = sqlite3.connect(self.name)

    @access
    def close(self):
        self.is_open = False
        self.conn.close()

    def get_data(self, query, params=None):
        self.conn = sqlite3.connect(self.name)
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        data = cursor.fetchall()
        self.conn.close()
        if not data:
            return [(0, )]
        return data
