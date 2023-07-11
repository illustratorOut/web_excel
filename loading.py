import openpyxl
from datetime import datetime


class Load_File_Excel:
    """Загрузка данных из excel файла и добавление в базу данных"""

    def __init__(self, pach):
        self.pach = pach
        self.exception = [None, 'None', '№', '', ' ', 'Произв', 'Номер', "/n"]
        self.data = []

    def loading_file(self):
        book = openpyxl.load_workbook(self.pach)
        sheet = book.active

        if sheet[10][0].value is None or sheet[10][3].value is None or sheet[10][26].value is None:
            return False
        else:
            for row in range(10, sheet.max_row):
                if sheet[row][0].value not in self.exception:
                    number = sheet[row][0].value
                    proizvod = sheet[row][26].value
                    art = f'{sheet[row][3].value}'
                    oders = sheet[row][4].value
                    description = sheet[row][5].value
                    qty = sheet[row][7].value
                    price1 = f'{sheet[row][11].value}'
                    barcode = '*000' + str(sheet[row][26].value).split('=')[0] + '/' + str(proizvod).split("=")[
                        11].replace(
                        str(oders).split("=")[0], "")
                    globalId = sheet[row][27].value
                    buyer = str(sheet[row][28].value).title()
                    userId = sheet[row][29].value
                    box = sheet[row][44].value

                    a = str(barcode.split('=')[:1])
                    b = str(barcode.split('=')[6:7])
                    repr(f'{a} / {b}')
                    xs = ''.join(proizvod.split('=')[1:2])
                    data = {
                        "number": number,
                        "proizvod": proizvod,
                        "art": art,
                        "description": description,
                        "oders": oders,
                        "qty": qty,
                        "price1": price1,
                        "barcode": barcode,
                        "globalId": globalId,
                        "buyer": buyer,
                        "userId": userId,
                        "box": box,
                        "xs": xs
                    }
                    self.data.append(data)
            return True

    def save_in_db(self, Item, db):
        for item in self.data:
            items = Item(title=item["art"].upper(),
                         description=item["description"],
                         qty=item["qty"],
                         price=item["price1"],
                         oders=item["oders"],
                         time=datetime.today(),
                         proizvod=item["xs"],
                         status='Непринят',
                         barcode=item["barcode"],
                         globalId=item["globalId"],
                         buyer=item["buyer"],
                         userId=item["userId"],
                         box=item["box"])
            db.session.add(items)
            db.session.commit()
