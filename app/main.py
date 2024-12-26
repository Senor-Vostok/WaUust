import os
from flask import Flask, render_template, request
from update_sql import ManagerSQL
import math

app = Flask(__name__)
mysql_host = os.getenv('MYSQL_HOST', 'mysql_db')
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', '1290AbUl17!')
mysql_database = os.getenv('MYSQL_DATABASE', 'uust_db')
manager = ManagerSQL(username=mysql_user, password=mysql_password, host=mysql_host, database=mysql_database)
manager.open()
manager.scrap()


def calculate_popularity(x):
    budget_places = x[4]
    paid_places = x[5]
    price = manager.get_data('SELECT price FROM po_paid WHERE code=:code AND profile=:profile',
                             {'code': x[0], 'profile': x[2]})[0][0]
    average_score = manager.get_data('SELECT average FROM sl_years WHERE code=:code AND name=:name', {'code': x[0], 'name': x[1]})[0][0]
    w1, w2, w3, w4 = 1.5, 1.0, 0.1, 0.05
    popularity = ((w1 * average_score + w2 * price + w4 * paid_places) / (1 + math.exp(-(w3 * budget_places))))
    return popularity


def get_item(rule, params, exist):
    item = manager.get_data(rule, params)[0][0]
    return item if item != 0 else exist


@app.route('/')
def hello():
    massive_areas = manager.get_data('SELECT * FROM aos_person')
    pop_max = max(calculate_popularity(i) for i in massive_areas)
    direction = [
        {
            "code": f"{i[0]}",
            "name": f"{i[2]}",
            "popularity": f"{int((calculate_popularity(i) / pop_max) * 10)} / 10",
            "min_avg_score": f"{get_item('SELECT average FROM sl_years WHERE code=:code AND name=:name', {'code': i[0], 'name': i[1]}, 'отсутствует')}",
            "cost": f"{manager.get_data('SELECT price FROM po_paid WHERE code=:code AND (profile=:profile OR name=:name)', {'code': i[0], 'profile': i[2], 'name': i[1]})[0][0]} р",
            "budget_places": f"{i[4]}"
        }
        for i in massive_areas
    ]
    return render_template('helloscreen.html', direction=direction)


@app.route('/test')
def test():
    massive_areas = manager.get_data('SELECT * FROM aos_person')
    result = sorted(massive_areas, key=lambda x: calculate_popularity(x), reverse=True)
    facultative = set(i[0] for i in manager.get_data("SELECT facultative FROM aos_person") if i[0])
    data = [
        {
            "title": f"{i[0]}\\n{i[1]}",
            "description": f"Профиль: {i[2]}\\n\\nФакультет: {i[3]}\\n\\n"
                           f"Минимальный средний балл: {get_item('SELECT average FROM sl_years WHERE code=:code AND name=:name', {'code': i[0], 'name': i[1]}, 'отсутствует')}\\n"
                           f"Общее количество бюджетных мест: {i[4]}\\n"
                           f"Стоимость обучения на платной основе: {manager.get_data('SELECT price FROM po_paid WHERE code=:code AND (profile=:profile OR name=:name)', {'code': i[0], 'profile': i[2], 'name': i[1]})[0][0]} р"
        }
        for i in result
    ]
    return render_template('base.html', data=data, facultative=facultative)


@app.route('/update-data', methods=['POST'])
def update_data() -> str:
    category = request.form.get('category', 'all')
    sort = request.form.get('sort', 'title-asc')
    if category == "all":
        massive_areas = manager.get_data('SELECT * FROM aos_person')
    else:
        massive_areas = manager.get_data(f'SELECT * FROM aos_person WHERE facultative="{category}"')
    if sort == 'popularity':
        result = sorted(massive_areas, key=lambda x: calculate_popularity(x), reverse=True)
    elif sort == 'score':
        result = sorted(massive_areas, key=lambda x: -(
            get_item('SELECT average FROM sl_years WHERE code=:code AND name=:name', {'code': x[0], 'name': x[1]}, 0)))
    elif sort == "price":
        result = sorted(massive_areas, key=lambda x: -(
            manager.get_data('SELECT price FROM po_paid WHERE code=:code AND (profile=:profile OR name=:name)',
                             {'code': x[0], 'profile': x[2], 'name': x[1]})[0][0]))
    elif sort == "budget":
        result = sorted(massive_areas, key=lambda x: x[4], reverse=True)
    facultative = set(i[0] for i in manager.get_data("SELECT facultative FROM aos_person") if i[0])
    data = [
        {
            "title": f"{i[0]}\\n{i[1]}",
            "description": f"Профиль: {i[2]}\\n\\nФакультет: {i[3]}\\n\\n"
                           f"Минимальный средний балл: {get_item('SELECT average FROM sl_years WHERE code=:code AND name=:name', {'code': i[0], 'name': i[1]}, 'отсутствует')}\\n"
                           f"Общее количество бюджетных мест: {i[4]}\\n"
                           f"Стоимость обучения на платной основе: {manager.get_data('SELECT price FROM po_paid WHERE code=:code AND (profile=:profile OR name=:name)', {'code': i[0], 'profile': i[2], 'name': i[1]})[0][0]} р"
        }
        for i in result
    ]
    return render_template('base.html', data=data, facultative=facultative)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
