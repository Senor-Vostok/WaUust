from flask import Flask, render_template, request
from build.update_sql import ManagerSQL
import math

app = Flask(__name__)


def calculate_popularity(x):
    budget_places = x[4]
    paid_places = x[5]
    price = manager.get_data('SELECT price FROM po_paid WHERE code=? AND profile=?', (x[0], x[2]))[0][0]
    average_score = manager.get_data('SELECT average FROM sl_years WHERE code=? AND name=?', (x[0], x[1]))[0][0]
    w1, w2, w3, w4 = 1.5, 1.0, 0.1, 0.05
    popularity = ((w1 * average_score + w2 * price + w4 * paid_places) / (1 + math.exp(-(w3 * budget_places))))
    return popularity


def get_item(rule, params, exist):
    item = manager.get_data(rule, params)[0][0]
    if item == 0:
        return exist
    return item


@app.route('/')
def testing():
    massive_areas = manager.get_data('SELECT * FROM aos_person')
    result = sorted(massive_areas, key=lambda x: calculate_popularity(x))
    result.reverse()
    data = [{"title": f"{i[0]}\\n{i[1]}", "description": f"Профиль: {i[2]}\\n\\nФакультет: {i[3]}\\n\\n"
             f"Минимальный средний балл: {get_item('SELECT average FROM sl_years WHERE code=? AND name=?', (i[0], i[1]), 'отсутствует')}\\n"
             f"Общее количество бюджетных мест: {i[4]}\\n"
             f"Стоимость обучения на платной основе: {manager.get_data('SELECT price FROM po_paid WHERE code=? AND (profile=? OR name=?)',(i[0], i[2], i[1]))[0][0]} р"} for i in result]
    return render_template('base.html', data=data)


if __name__ == "__main__":
    manager = ManagerSQL('uust.db')
    manager.open()
    app.run()
