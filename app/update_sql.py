from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import requests
from bs4 import BeautifulSoup
from functools import wraps

urls = {
    "areas of study": "https://uust.ru/admission/bachelor-and-specialist/adm-plan/2024/",
    "prices_of_paid": "https://uust.ru/admission/bachelor-and-specialist/tuition-fees/2024/",
    "score_last_years": "https://uust.ru/admission/bachelor-and-specialist/passing-scores/2024/"
}

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
        self.engine = create_engine(f'sqlite:///{name}')
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = None

        # Define tables
        self.areas_of_study = Table(
            'aos_person', self.metadata,
            Column('code', String, nullable=False),
            Column('name', String, nullable=False),
            Column('profile', String, nullable=False),
            Column('facultative', String, nullable=False),
            Column('count_budget', Integer, nullable=False),
            Column('count_paid', Integer, nullable=False)
        )

        self.prices_of_paid = Table(
            'po_paid', self.metadata,
            Column('code', String, nullable=False),
            Column('name', String, nullable=False),
            Column('profile', String, nullable=False),
            Column('price', Integer, nullable=False)
        )

        self.score_last_years = Table(
            'sl_years', self.metadata,
            Column('code', String, nullable=False),
            Column('name', String, nullable=False),
            Column('average', Integer, nullable=False)
        )

        self.metadata.create_all(self.engine)

    @staticmethod
    def access(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.session:
                return func(self, *args, **kwargs)
            else:
                print("В доступе отказано")
                return None

        return wrapper

    def open(self):
        self.session = self.Session()

    @access
    def close(self):
        self.session.close()
        self.session = None

    @access
    def scrap(self):
        for do in urls:
            url = urls[do]
            if do == 'areas of study':
                table_data = get_table(url=url)[0][4:]
                data = []
                for area in table_data:
                    has_code = (((area[0].split())[0]).split('.'))[0].isdigit()
                    if has_code:
                        code, name = (area[0].split())[0], ' '.join((area[0].split())[1:])
                        profile = area[1]
                        facultative = area[2]
                        count_budget = int(area[3]) if area[3] else 0
                        count_paid = int(area[8]) if area[8] else 0
                    else:
                        code, name = data[-1]['code'], data[-1]['name']
                        profile = area[0]
                        facultative = area[1]
                        count_budget = int(area[2]) if area[2] else 0
                        count_paid = int(area[7]) if area[7] else 0
                    if count_paid != 0 or count_budget != 0:
                        data.append({'code': code, 'name': name, 'profile': profile, 'facultative': facultative, 'count_budget': count_budget, 'count_paid': count_paid})
                self.session.execute(self.areas_of_study.insert(), data)

            elif do == "prices_of_paid":
                tables = get_table(url=url)[:2]
                data = []
                for table in tables:
                    for line in table[2:]:
                        if line[3] == "Очная":
                            code, name, profile, price = line[0], line[1], line[2], int(line[4])
                            data.append({'code': code, 'name': name, 'profile': profile, 'price': price})
                self.session.execute(self.prices_of_paid.insert(), data)

            elif do == "score_last_years":
                tables = get_table(url=url)[:2]
                data = []
                for table in tables:
                    for line in table[1:]:
                        average = [int(i) for i in line[2:] if i.isdigit()]
                        code, name, average = line[0], line[1], sum(average) // len(average)
                        data.append({'code': code, 'name': name, 'average': average})
                self.session.execute(self.score_last_years.insert(), data)

        self.session.commit()

    @access
    def get_data(self, query, params=None):
        if params and not isinstance(params, dict):
            params = dict(enumerate(params))
        result = self.session.execute(text(query), params if params else {}).fetchall()
        return result if result else [(0,)]
