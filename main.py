from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import shutil

from SqliteHelper import *
import tread_server
from localtime import *
import config

SELECT_QUERY = 'SELECT id, type, symbols_plate, region, strftime("%H:%M:%S %d.%m.%Y", datetime(date, "unixepoch", "localtime")) as date, media FROM "license_plates" ORDER BY '

currentRow = None
current_mode_sorting = {"type": "id", "reverse": 0}
HorizontalHeaderItems_default = ['№ записи', 'Тип транспорта', 'Номер', 'Регион', 'Дата записи', 'Размер вложения']
current_mediaPath = "./"
media = None
media_size = [488, 249]
temporary_file_path = None
known_media_id = []
selected_row = -1

def size_calculation(data):
    size = len(data)
    if size >= 1024:
        size = size / 1024
        if size % 1:
            size = str(int(size) + 1)
        if len(size) > 3:
            size_formatted = ""
            for count, number in enumerate(reversed(size), start = 1):
                size_formatted = number + size_formatted
                if count % 3 == 0:
                    size_formatted = " " + size_formatted
        else:
            size_formatted = size
    elif size > 0:
        size_formatted = "1"
    else:
        size_formatted = "0"
    return size_formatted + " КБ"

def loadData(mode = {"type": "id", "reverse": 0}):
    if mode["reverse"] == 0:
        sorting_direction = "ASC"
    else:
        sorting_direction = "DESC"
    if mode["type"] not in ["date", "media"]:
        license_plates = helper.select(SELECT_QUERY + mode["type"] + ' ' + sorting_direction)
    elif mode["type"] == "date":
        license_plates = helper.select(SELECT_QUERY + 'date ' + sorting_direction)
    elif mode["type"] == "media":
        license_plates = helper.select(SELECT_QUERY + 'length(media) ' + sorting_direction)
    
    row_number = 0
    for row_number, row_in_license_plates in enumerate(license_plates):
        dlg.tableWidget.insertRow(row_number)
        for column_number, data in enumerate(row_in_license_plates):
            if column_number != 5:
                cell_data = str(data)
            else:
                cell_data = size_calculation(data)
            cell = QtWidgets.QTableWidgetItem(cell_data)
            dlg.tableWidget.setItem(row_number, column_number, cell)
    return row_number
    
def scrollTo(row = None):
    dlg.tableWidget.scrollToItem(dlg.tableWidget.selectRow(row))

def clearData():
    dlg.tableWidget.clearSelection()
    while(dlg.tableWidget.rowCount()>0):
        dlg.tableWidget.removeRow(0)
        dlg.tableWidget.clearSelection()

def addInput():
    date = get_unixtime()
    symbols_plate = dlg.lineEdit_symbols_plate.text()
    region = dlg.lineEdit_region.text()
    type = dlg.lineEdit_type.text()
    global media
    
    if symbols_plate.strip(" ") != "" and region.strip(" ") != "":
        input_data = (type, symbols_plate, int(region), date, media)
        helper.insert("INSERT INTO license_plates (type, symbols_plate, region, date, media) VALUES(?,?,?,?,?)", input_data)
        new_row = reload_table()
        scrollTo(new_row)
    else:
        show_message("Ошибка записи", "Проверьте вводимые данные.")

def ViewMedia(widget, media_path, width, height):
    if media_path:
        pixmap = QPixmap(media_path)
        pixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        widget.setPixmap(pixmap)

def selectionChanged():
    global selected_row
    selected_row = getSelectedRowId()
    id = dlg.tableWidget.item(selected_row, 0).text()
    type = dlg.tableWidget.item(selected_row, 1).text()
    symbols_plate = dlg.tableWidget.item(selected_row, 2).text()
    region = dlg.tableWidget.item(selected_row, 3).text()
    global media
    try:
        media = helper.select('SELECT media FROM "license_plates" WHERE id=' + id)[0][0]
    except IndexError:
        pass #нет вложения
    
    dlg.lineEdit_symbols_plate.setText(symbols_plate)
    dlg.lineEdit_region.setText(region)
    dlg.lineEdit_type.setText(type)
    
    global temporary_file_path
    temporary_file_path = "Temp/{}.jpg".format(id)
    
    global known_media_id
    if id not in known_media_id:
        try:
            with open(temporary_file_path, 'wb') as temporary_file:
                temporary_file.write(media)
                known_media_id.append(id)
        except FileNotFoundError:
            show_message("Ошибка", "Невозможно отобразить изображение.\nНет доступа к временным файлам.")
            return None
    
    global media_size
    ViewMedia(dlg.label_media, temporary_file_path, media_size[0], media_size[1])

def getSelectedRowId():
    return dlg.tableWidget.currentRow()

def getSelectedInputId():
    id_update_item = dlg.tableWidget.item(getSelectedRowId(),0)
    if id_update_item == None:
        return "0"
    return id_update_item.text()

def deleteInput():
    id_delete = getSelectedInputId()
    helper.delete("DELETE FROM license_plates WHERE id ="+id_delete)
    last_row = reload_table()
    global currentRow
    if currentRow > last_row:
        scrollTo(last_row)

def updateInput():
    id_update = getSelectedInputId()
    
    type = dlg.lineEdit_type.text()
    symbols_plate = dlg.lineEdit_symbols_plate.text()
    region = dlg.lineEdit_region.text()
    global media
    global known_media_id
    
    if id_update in known_media_id:
        known_media_id.pop(known_media_id.index(id_update))
    
    if symbols_plate.strip(" ") != "" and region.strip(" ") != "":
        input_data = (type, symbols_plate, int(region), media)
        helper.edit("UPDATE license_plates SET type=?, symbols_plate=?, region=?, media=? WHERE id="+id_update, input_data)
        reload_table()
    else:
        show_message("Ошибка записи", "Проверьте вводимые данные.")
        
def importMedia():
    global current_mediaPath
    file_path = QFileDialog.getOpenFileName(None, "Открытие", current_mediaPath)[0]
    if file_path:
        current_mediaPath = file_path[ : file_path.rfind("/")]
        global temporary_file_path
        global media_size
        temporary_file_path = file_path
        with open(file_path, "rb") as file:
            global media
            media = file.read()
        ViewMedia(dlg.label_media, temporary_file_path, media_size[0], media_size[1])

def exportMedia():
    global selected_row
    selected_row = getSelectedRowId()
    if selected_row != -1:
        global current_mediaPath
        id = dlg.tableWidget.item(selected_row, 0).text()
        type = dlg.tableWidget.item(selected_row, 1).text()
        symbols_plate = dlg.tableWidget.item(selected_row, 2).text()
        region = dlg.tableWidget.item(selected_row, 3).text()
        file_name = "{0}/{1}_{2}{3}_id{4}.jpg".format(current_mediaPath, type, symbols_plate, region, id)
        file_path = QFileDialog.getSaveFileName(None, "Сохранение", file_name)[0]
        if file_path:
            try:
                shutil.copy("Temp/{}.jpg".format(id), file_path)
            except Exception as Error:
                show_message("Ошибка", "Не удалось сохранить файл.\n"+str(Error))
    else:
        show_message("Экспортирование файла", "Сначала выберите изображение.")

def reload_table(mode = {"type": "id", "reverse": 0}):
    global currentRow
    currentRow = getSelectedRowId()
    
    clearData()
    dlg.lineEdit_symbols_plate.setText("")
    dlg.lineEdit_region.setText("")
    dlg.lineEdit_type.setText("")
    dlg.label_media.setText("Просмотр изображения")
    global temporary_file_path
    temporary_file_path = None
    
    last_row = loadData(mode)
    scrollTo(currentRow)
    return last_row
    
def button_reload_table():
    global known_media_id
    global current_mode_sorting
    known_media_id = []
    reload_table(current_mode_sorting)
    dlg.tableWidget.resizeColumnsToContents()

def check_mode_sorting(current_mode, new_mode_str):
    if current_mode["type"] == new_mode_str:
        if current_mode["reverse"] == 0:
            current_mode.update({"reverse": 1})
        else:
            current_mode.update({"reverse": 0})
    else:
        current_mode.update({"type": new_mode_str, "reverse": 0})
    return current_mode

def sorting(number_column):
    global current_mode_sorting
        
    if number_column == 0:
        new_mode_str = "id"
    elif number_column == 1:
        new_mode_str = "type"
    elif number_column == 2:
        new_mode_str = "symbols_plate"
    elif number_column == 3:
        new_mode_str = "region"
    elif number_column == 4:
        new_mode_str = "date"
    elif number_column == 5:
        new_mode_str = "media"
    
    current_mode_sorting = check_mode_sorting(current_mode_sorting, new_mode_str)
    
    global HorizontalHeaderItems_default
    HorizontalHeaderLabels = HorizontalHeaderItems_default.copy()
    HorizontalHeaderLabels[number_column] = HorizontalHeaderLabels[number_column] + (" ▼" if current_mode_sorting["reverse"] == 0 else " ▲")
    dlg.tableWidget.setHorizontalHeaderLabels(HorizontalHeaderLabels)
    
    reload_table(current_mode_sorting)
    dlg.tableWidget.resizeColumnsToContents()
    
def ResizeMediaLabel(event):
    global media_size
    media_size = [event.size().width(), event.size().height()]
    global temporary_file_path
    ViewMedia(dlg.label_media, temporary_file_path, media_size[0], media_size[1])

def changeResizeEvent(widget, func):
    widget.resizeEvent = func

def show_message(title="Error", message="Infromation"):
    QMessageBox.information(None, title, message)

def start_server():
    try:
        tread_server.create_thread()
    except Exception as Error:
        show_message("Ошибка", "Не удалось запустить сервер.\n"+str(Error))


if __name__ == '__main__':
    print("Запуск: {}\n".format(time_formatted()))
    
    try:
        os.mkdir("Temp")
        with open("Temp/Powered_by_Data_Processing_System", "w") as check_folder_by_file:
            check_folder_by_file.write("")
    except OSError:
        pass
    
    app = QtWidgets.QApplication([])
    dlg = uic.loadUi(config.UI_filename)
    dlg.setWindowTitle(config.UI_title)

    helper = SqliteHelper(config.DB_filename)
    
    dlg.tableWidget.itemSelectionChanged.connect(selectionChanged)
    dlg.tableWidget.horizontalHeader().sectionClicked.connect(sorting)
    
    dlg.pushButton.clicked.connect(addInput)
    dlg.pushButton_del.clicked.connect(deleteInput)
    dlg.pushButton_update.clicked.connect(updateInput)
    dlg.pushButton_import.clicked.connect(importMedia)
    dlg.pushButton_export.clicked.connect(exportMedia)
    dlg.pushButton_reload.clicked.connect(button_reload_table)

    changeResizeEvent(dlg.label_media, ResizeMediaLabel)
    
    start_server()

    loadData()
    
    HorizontalHeaderLabels = HorizontalHeaderItems_default.copy()
    HorizontalHeaderLabels[0] = HorizontalHeaderLabels[0] + " ▼"
    dlg.tableWidget.setHorizontalHeaderLabels(HorizontalHeaderLabels)
    
    dlg.setStyleSheet("font-size: 11px")
    
    dlg.tableWidget.resizeColumnsToContents()
    dlg.tableWidget.verticalHeader().setVisible(False)
    

    dlg.show()
    app.exec()
    
    try:
        with open("Temp/Powered_by_Data_Processing_System", "r"):
            pass
        shutil.rmtree("Temp")
    except Exception as Error:
        print("\nПроизошла ошибка\nНе удалось очистить временные файлы. Они будут удалены при следующей работе.\nМожете очистить самостоятельно, удалив папку Temp из места запуска программы.\n\nКод ошибки: " + str(Error))
        input("\nНажмите любую клавишу, чтобы закрыть программу...")