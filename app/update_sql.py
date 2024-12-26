from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import requests
from bs4 import BeautifulSoup
from functools import wraps

urls = {
    "areas_of_study": "https://uust.ru/admission/bachelor-and-specialist/adm-plan/2024/",
    "prices_of_paid": "https://uust.ru/admission/bachelor-and-specialist/tuition-fees/2024/",
    "score_last_years": "https://uust.ru/admission/bachelor-and-specialist/passing-scores/2024/"
}

Base = declarative_base()


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


class AosPerson(Base):
    __tablename__ = 'aos_person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    profile = Column(String(255), nullable=False)
    facultative = Column(String(255), nullable=False)
    count_budget = Column(Integer, nullable=False)
    count_paid = Column(Integer, nullable=False)


class PoPaid(Base):
    __tablename__ = 'po_paid'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    profile = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)


class SlYears(Base):
    __tablename__ = 'sl_years'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    average = Column(Integer, nullable=False)


class ManagerSQL:
    def __init__(self, username, password, host, database):
        self.username = username
        self.password = password
        self.host = host
        self.database = database
        self.engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}?charset=utf8mb4')
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = None
        self.create_database()
        Base.metadata.create_all(self.engine)

    def create_database(self):
        engine = create_engine(f'mysql+pymysql://{self.username}:{self.password}@{self.host}')
        with engine.connect() as conn:
            conn.execute(text(
                f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))

    @staticmethod
    def access(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.session:
                return func(self, *args, **kwargs)
            else:
                print("В доступе отказано. Сессия не открыта.")
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
        all_data = {}
        for do in urls:
            url = urls[do]
            all_data[do] = get_table(url=url)
        data_areas_of_study = []
        data_prices_of_paid = []
        data_score_last_years = []
        for area in all_data["areas_of_study"][0][4:]:
            has_code = (((area[0].split())[0]).split('.'))[0].isdigit()
            if has_code:
                code, name = (area[0].split())[0], ' '.join((area[0].split())[1:])
                profile = area[1]
                facultative = area[2]
                count_budget = int(area[3]) if area[3] else 0
                count_paid = int(area[8]) if area[8] else 0
            else:
                code, name = data_areas_of_study[-1]['code'], data_areas_of_study[-1]['name']
                profile = area[0]
                facultative = area[1]
                count_budget = int(area[2]) if area[2] else 0
                count_paid = int(area[7]) if area[7] else 0
            if count_paid != 0 or count_budget != 0:
                data_areas_of_study.append({'code': code, 'name': name, 'profile': profile, 'facultative': facultative,
                                            'count_budget': count_budget, 'count_paid': count_paid})
        for table in all_data["prices_of_paid"][:2]:
            for line in table[2:]:
                if line[3] == "Очная":
                    code, name, profile, price = line[0], line[1], line[2], int(line[4])
                    data_prices_of_paid.append({'code': code, 'name': name, 'profile': profile, 'price': price})
        for table in all_data["score_last_years"][:2]:
            for line in table[1:]:
                average = [int(i) for i in line[2:] if i.isdigit()]
                code, name, average = line[0], line[1], sum(average) // len(average)
                data_score_last_years.append({'code': code, 'name': name, 'average': average})
        try:
            self.session.bulk_insert_mappings(AosPerson, data_areas_of_study)
            self.session.bulk_insert_mappings(PoPaid, data_prices_of_paid)
            self.session.bulk_insert_mappings(SlYears, data_score_last_years)
            self.session.commit()
        except Exception as e:
            print(f"Ошибка при вставке данных: {e}")
            self.session.rollback()

    @access
    def get_data(self, query, params=None):
        if params and not isinstance(params, dict):
            params = dict(enumerate(params))
        result = self.session.execute(text(query), params if params else {}).fetchall()
        return result if result else [(0,)]
