import time
import os
from modul_file import file_extension
from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta, datetime
from loading import Load_File_Excel
from modul_render_photo import get_developer_info
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    oders = db.Column(db.String(100), nullable=False)
    time = db.Column(db.Date, default=datetime.utcnow)
    proizvod = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(100), nullable=False)
    globalId = db.Column(db.String(100), nullable=False)
    buyer = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.String(100), nullable=False)
    box = db.Column(db.String(100), nullable=False)
    # isActive = db.Column(db.Boolean, default=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('Table_loading.id'))


class TableLoading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, default=datetime.utcnow)
    time = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self) -> str:
        return self.title


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        search = request.form['search_art'].strip()
        search_art = Item.query.order_by(
            Item.price).filter_by(title=f'{search}')
        input_select = request.form.get("select1")

        if search == '':
            """Нужно написать ограничение для вывода только 25 шт. """
            search_art2 = Item.query.order_by(Item.time.desc()).all()
            return render_template('search.html', data2=search_art2, option1='selected', value1=search)

        if input_select == str(1):
            d = datetime.today() - timedelta(days=31)
            gg = d.strftime('%d-%m-%Y')
            print(gg)

            search_art = Item.query.filter_by(
                title=f'{search}').filter(Item.time >= d)
            return render_template('search.html', data2=search_art, option1='selected', value1=search)

        if input_select == str(2):
            d = datetime.today() - timedelta(days=90)
            gg = d.strftime('%d-%m-%Y')
            print(gg)

            search_art = Item.query.filter_by(
                title=f'{search}').filter(Item.time >= f'{d}')
            return render_template('search.html', data2=search_art, option2='selected', value1=search)

        if input_select == str(3):
            d = datetime.today() - timedelta(days=365)
            gg = d.strftime('%d-%m-%Y')
            print(gg)

            search_art = Item.query.filter_by(title=f'{search}').filter(
                (Item.time >= f'{d}') | (Item.time <= f'{d}'))
            return render_template('search.html', data2=search_art, option3='selected', value1=search)

        return render_template('search.html', data2=search_art, option1='selected')

    else:
        return render_template('search.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == "POST":

        title = request.form['title']
        price = request.form['price']
        time = request.form['time']

        # Переобразование type str в <class 'datetime.datetime'>
        dt = datetime.strptime(time, '%Y-%m-%d').date()

        item = Item(title=title, price=price, time=dt, proizvod='1', qty=1, status='Непринят')

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка =("
    else:
        return render_template('add.html', newdata=date.today())


@app.route('/loading', methods=['POST', 'GET'])
def loading():
    if request.method == "POST":
        current_date_time = datetime.today()
        f = request.files['input_loading']
        expansion = f.filename.split(".")[-1]
        pach_file = f"files/{f.filename}"

        obj = request.files['input_loading'].read()

        if "xls" == expansion:
            Table = TableLoading(title=f.filename, data=current_date_time, time=current_date_time)
            db.session.add(Table)
            db.session.commit()

            with open(pach_file, "wb") as fp:
                fp.write(obj)

            name = file_extension(pach_file)

            file = Load_File_Excel(name)
            a = file.loading_file()

            if a:
                file.save_in_db(Item, db)
                return render_template('loading.html', f=f'Файл загружен: {f.filename}', hidden='', hidden1='hidden')
            else:
                pass

        elif "xlsx" == expansion:
            Table = TableLoading(title=f.filename, data=current_date_time, time=current_date_time)
            db.session.add(Table)
            db.session.commit()

            file = Load_File_Excel(f)
            a = file.loading_file()

            if a:
                file.save_in_db(Item, db)
                return render_template('loading.html', f=f'Файл загружен: {f.filename}', hidden='', hidden1='hidden')
            else:
                pass

        return render_template('loading.html', hidden='hidden', hidden1='')
    else:
        return render_template('loading.html', hidden='hidden', hidden1='')


# Обработчик кнопки подробнее
@app.route('/<name>/<int:id>', methods=['POST', 'GET'])
def buy(name, id, ):
    search_art = Item.query.get(id)

    photo = get_developer_info(name)

    if photo is not None:
        print("-----------------")
        with open("static/avatar.png", "wb") as f:
            f.write(photo)

    return render_template('buy.html', name=name, search_art=search_art, photo=photo)


# Функция приема товара
@app.route('/product/<time>', methods=['POST', 'GET'])
def product(time):
    if request.method == "POST":
        try:
            # Добавить звук приема товара
            search = request.form['search_art'].strip()
            search_art = Item.query.filter(Item.time == f'{time}').filter(Item.barcode.contains(search))

            # id = Item.query.filter(Item.time == f'{time}').filter(Item.barcode == search).first()
            # print(id)

            db.session.query(Item).filter(Item.time == f'{time}').filter(Item.barcode == search).update(
                {Item.status: "Принят"},
                synchronize_session=False)
            db.session.commit()
        except:
            # Добавить звук ошибки
            print(f"ошибка -------------{search_art}")

    search_art = Item.query.filter(Item.time == f'{time}').all()
    qty = Item.query.filter(Item.time == f'{time}').count()
    count = Item.query.filter(Item.time == f'{time}').filter(Item.status == "Принят").count()

    return render_template('product.html', date3=search_art, qty=qty, count=count)


# Отображение коробок
@app.route('/box', methods=['POST', 'GET'])
def box():
    search_art2 = Item.query.all()
    box = Item.query.filter(Item.box == Item.box).all()

    new_list = []
    for i in box:
        if i.box not in new_list:
            new_list.append(i.box)

    return render_template('box.html', date2=new_list)


@app.route('/product', methods=['POST', 'GET'])
def product_main():
    search_art = Item.query.filter(Item.time).all()
    result = set(i.time for i in search_art)
    qty = {i: Item.query.filter(Item.time == f'{i}').count() for i in sorted(list(result), reverse=True)}

    if request.method == "POST":
        # --------------------------
        input_select = request.form.get("select1")
        delta = datetime.today() - timedelta(days=int(input_select))
        current_data = delta.strftime('%Y-%m-%d')

        search_art = Item.query.filter(Item.time >= current_data)
        result = set(i.time for i in search_art)
        qty = {i: Item.query.filter(Item.time == f'{i}').count() for i in sorted(list(result), reverse=True)}
        return render_template('product_main.html', hidden='hidden', hidden1='', data2=qty)

    return render_template('product_main.html', hidden='hidden', hidden1='', data2=qty)


@app.route('/сlient', methods=['POST', 'GET'])
def client():
    if request.method == "POST":
        search = request.form['search_art'].strip()
        # search_art = Item.query.filter(Item.userId == search).filter(Item.status != "Принят")
        search_art = Item.query.filter(Item.userId == search)

        # art = Item.query.all()
        # for i in art:
        #     print(i.oders)
        #     if "нал" in i.oders:
        #         print("fdsgklfdngjhdfjklgndfjngjndfgj")

        if len(list(Item.query.filter(Item.userId == search))):
            return render_template('сlient.html', date3=search_art)

    return render_template('сlient.html')


@app.route('/save_excel/<userId>', methods=['POST', 'GET'])
def save_excel(userId):
    if request.method == "POST":
        search_art = Item.query.filter(Item.userId == userId)
        name = [i.buyer for i in search_art][0]

        import pandas as pd

        result = {'Артикул': [i.title for i in search_art],
                  'Производитель': [i.proizvod for i in search_art],
                  'Описание': [i.description for i in search_art],
                  'Количество': [i.qty for i in search_art],
                  'Цена': [i.price for i in search_art],
                  'Сумма': [i.price * i.qty for i in search_art],
                  'Дата загрузки': [str(i.time.strftime("%d-%m-%Y")) for i in search_art],
                  'UserId': [i.userId for i in search_art],
                  }

        df = pd.DataFrame(result)

        df.to_excel(f'./file_excel/{name}.xlsx')

        path = f"./file_excel/{name}.xlsx"
        return send_file(path, as_attachment=True)

    # return render_template('save_excel.html')


app.run(debug=True)
