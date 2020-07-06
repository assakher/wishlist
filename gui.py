import sys

from PyQt5 import QtCore
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableView, QGridLayout, QPushButton

import config as c  # imports connection parameters


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('Wishlist')

        self.create_central_widget()
        self.create_status_bar()

    def create_central_widget(self):
        central_widget = MainTable(self)
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готово")

    def update_status_bar(self, message):
        self.status_bar.showMessage(message)


class MainTable(QWidget):
    def __init__(self, parent):
        super(MainTable, self).__init__(parent)

        # connection to the database
        # uncomment to test with SQLite
        """db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('items.db')"""
        # connects to database using ODBC driver, possible to use MySQL driver
        db = QSqlDatabase.addDatabase('QODBC3')
        db.setDatabaseName('DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=%s;DATABASE=%s;UID=%s;'
                           % (c.hostname,
                              c.databasename,
                              c.username))
        if db.open():
            # adds required scheme to database
            query = QSqlQuery()
            query.exec_("""create table items (
                   id int auto_increment, 
                   name varchar(50) not null, 
                   price double not null default 0.0,
                   link varchar(100),
                   comment varchar(200),
                   constraint ID primary key (id))""")
        else:
            print("Couldn't load database")
            exit(1)

        self.initialize_model()

        self.table = TableView(self)
        self.applybtn = ApplyBtn(self)
        self.cancelbtn = CancelBtn(self)
        self.addrowbtn = AddRowBtn(self)
        self.delrowbtn = DelRowBtn(self)

        layout = QGridLayout()
        layout.addWidget(self.table, 0, 0, 2, 5)
        layout.addWidget(self.applybtn, 6, 0)
        layout.addWidget(self.cancelbtn, 6, 1)
        layout.addWidget(self.addrowbtn, 6, 3)
        layout.addWidget(self.delrowbtn, 6, 4)
        self.setLayout(layout)

    def initialize_model(self):
        # Model to render sql database into table
        self.model = QSqlTableModel()
        self.model.setTable("items")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Наименование")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Цена",)
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Ссылка")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Комментарий")


class TableView(QTableView):
    def __init__(self, parent):
        super(TableView, self).__init__(parent)
        self.setModel(self.parent().model)
        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
        self.adjustSize()
        # hides primary key from user
        self.hideColumn(0)


class ApplyBtn(QPushButton):
    def __init__(self, parent):
        super(ApplyBtn, self).__init__(parent)
        self.setText('Применить')
        self.clicked.connect(self.commit)

    def commit(self):
        self.parent().model.submitAll()
        self.parent().parent().update_status_bar("Изменения сохранены")


class CancelBtn(QPushButton):
    def __init__(self, parent):
        super(CancelBtn, self).__init__(parent)
        self.setText('Отменить')
        self.clicked.connect(self.rollback)

    def rollback(self):
        self.parent().model.revertAll()
        self.parent().model.select()
        self.parent().parent().update_status_bar("Отменено")


class AddRowBtn(QPushButton):
    def __init__(self, parent):
        super(AddRowBtn, self).__init__(parent)
        self.setText('Добавить запись')
        self.clicked.connect(self.addrow)

    def addrow(self):
        self.parent().model.insertRows(self.parent().model.rowCount(), 1)
        self.parent().parent().update_status_bar("Введите данные")


class DelRowBtn(QPushButton):
    def __init__(self, parent):
        super(DelRowBtn, self).__init__(parent)
        self.setText('Удалить запись')
        self.clicked.connect(self.delrow)

    def delrow(self):
        self.parent().model.removeRow(self.parent().table.currentIndex().row())
        self.parent().parent().update_status_bar("Запись удалена")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())
