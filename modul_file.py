import pyexcel as p


def file_extension(file: str) -> str:
    """
    Функция принемает путь к файлу xls создает файл с расширением xlsx
    и возвращает путь к ново созданному файлу
    """

    try:
        p.save_book_as(file_name=file, dest_file_name=f"{file}x")
        return f"{file}x"

    except:
        print(f"Ошибка при загрузке файла {file}")
