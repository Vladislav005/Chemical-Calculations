import sys
from PyQt5.QtGui import QTextTable, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel, QTableWidget, QWidget, \
    QLineEdit, QHBoxLayout, QTabWidget, QTableWidgetItem, QMessageBox, QMenu, QAbstractItemView, QToolBox, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import uic, QtWidgets
import json
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


import reliase
from reliase import Attempt, get_all_elements, crash, Experiment, add_attempt
from methods import *
from calc import *
import from_file_imports
import functions



# виджет попыток
class AttemptWidget(QWidget):
    def __init__(self, attempt: Attempt):
        super().__init__()

        self.ui = uic.loadUi('ui/AttemptWidget.ui', self)

        self.attempt = attempt

        #self.ui.addAttemptButton.clicked.connect(self.addAttempt)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ui.mainLayout.addWidget(self.canvas)
        self.drawChart()

        self.show_inits()
        self.show_results()

    def drawChart(self):
        method = get_method(self.attempt.func, self.attempt.id_method, self.attempt.id_exp)
        ax = self.figure.add_subplot(111)
        method.draw_chart(ax)
        self.canvas.draw()

    def show_inits(self):
        self.ui.initTextBrowser.append(f'№ Эксп.: {self.attempt.id_exp}')
        for item in self.attempt.init.items():
            self.ui.initTextBrowser.append(f'{item[0]}: {item[1]}')

    def show_results(self):
        for item in self.attempt.result.items():
            if type(item[1]) == list:
                for i in item[1]:
                    self.ui.resultTextBrowser.append(f'{i}\n')
            elif type(item[1]) == dict:
                for i in item[1]:
                    self.ui.resultTextBrowser.append(f'{i}\n')
            else:
                self.ui.resultTextBrowser.append(f'{item[0]}: {item[1]}\n')

    def addAttempt(self):
        self.attempt.add_into_global_bd()


# окно для добавления экспериментов
class AddExperimentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('ui/AddExperimentWindow.ui', self)

        self.ui.add_button.clicked.connect(self.add_button_clicked)

    # обработка нажатия кнопки "Добавить"
    def add_button_clicked(self):
        first_element = self.ui.lineEdit.text()
        second_element = self.ui.lineEdit_2.text()
        temperature = self.ui.lineEdit_3.text()
        x2 = self.ui.textEdit.toPlainText().split('\n')
        PkPa = self.ui.textEdit_2.toPlainText().split('\n')
        dPPa = self.ui.textEdit_5.toPlainText().split('\n')
        y1 = self.ui.textEdit_3.toPlainText().split('\n')
        y2 = self.ui.textEdit_4.toPlainText().split('\n')
        GEJ = self.ui.textEdit_6.toPlainText().split('\n')
        x2 = list(filter(('').__ne__, x2))
        PkPa = list(filter(('').__ne__, PkPa))
        dPPa = list(filter(('').__ne__, dPPa))
        y1 = list(filter(('').__ne__, y1))
        y2 = list(filter(('').__ne__, y2))
        GEJ = list(filter(('').__ne__, GEJ))
        source_data = {'x2': x2, 'PkPa':PkPa, 'dPPa':dPPa, 'y1':y1, 'y2':y2, 'GEJ':GEJ}
        article = self.ui.lineEdit_4.text()
        if (first_element != '' and second_element != '' and temperature != '' and x2 != [] and PkPa != [] and dPPa != [] and y1 != [] and y2 != [] and GEJ != [] and article != ''):
            exp = Experiment(first_element, second_element, temperature, source_data, article)
            exp.add_into_db()
            self.ui.error_label.setText('')
            self.ui.lineEdit.setText('')
            self.ui.lineEdit_2.setText('')
            self.ui.lineEdit_3.setText('')
            self.ui.lineEdit_4.setText('')
            self.ui.textEdit.setPlainText('')
            self.ui.textEdit_2.setPlainText('')
            self.ui.textEdit_3.setPlainText('')
            self.ui.textEdit_4.setPlainText('')
            self.ui.textEdit_5.setPlainText('')
            self.ui.textEdit_6.setPlainText('')
        else:
            self.ui.error_label.setText("Не все поля заполнены")



# окно с информацией об эксперименте
class ExperimentInfoDialog(QDialog):
    def __init__(self, id_experiments: list):
        super().__init__()

        self.ui = uic.loadUi('ui/experimentInfoDialog.ui', self)

        self.id_experiments = id_experiments
        self.showInfo()

    def showInfo(self):
        for id_exp in self.id_experiments:
            inform = reliase.get_experiment_as_id(id_exp)
            for item in inform.items():
                self.ui.listWidget.addItem(f'{item[0]}: {item[1]}')
            self.ui.listWidget.addItem('\n')


# окно с фильтрами экспериментов для поиска по элементам
class FiltersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/FiltersDialog.ui')


# окно для открытия файла для импорта данных эксперимента
class ImportExperimentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/ImportExperimentDialog.ui', self)
        self.ui.fileDialogButton.clicked.connect(self.open_path_dialog)
        self.ui.addButton.clicked.connect(self.add_button_clicked)


    def open_path_dialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*.csv *.xlsx);;CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        self.ui.pathLineEdit.setText(fileName)
    
    def correct_file_directory_check(self, file_path: str) -> bool:
        import os.path
        return os.path.exists(file_path)

    def add_button_clicked(self):
        if self.correct_file_directory_check(self.ui.pathLineEdit.text()):
            exp = from_file_imports.get_experiment_from_csv(self.ui.pathLineEdit.text())
            exp.add_into_db()
        else:
            self.file_path_error()
    
    def file_path_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Некорректный путь к файлу")
        msg.setInformativeText('Путь к файлу введен неверно или файла с таким путем не существует')
        msg.setWindowTitle("Сообщение об ошибке")
        msg.exec_()



#   ОСНОВНОЕ ОКНО   ##################################################################################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('ui/UiForChem.ui', self)

        # для экспериментов
        self.ui.add_button.clicked.connect(self.add_button_clicked)
        self.ui.update_button_experiments.clicked.connect(self.update_table_experiments)
        self.ui.filterButton.clicked.connect(self.filterButton_clicked)
        self.ui.swapButton.clicked.connect(self.swapButtonClicked)

        self.create_table_experiments()
        self.ui.experimentsTab.clicked.connect(self.clicked_on_experiments_tab)

        self.current_row = -1

        # для расчетов
        self.makeCalculatePage()

        # для статей
        self.show_articles()

        # для элементов
        self.ui.update_button_elements.clicked.connect(self.create_table_elements)

        self.create_table_elements()


    # создание таблицы экспериментов
    def create_table_experiments(self, first_element_filter: str = None, second_element_filter: str = None):
        if (first_element_filter == None or first_element_filter == ''):
            first_element_filter = 'Any'
        if (second_element_filter == None or second_element_filter == ''):
            second_element_filter = 'Any'

        first_element_list = reliase.get_elements_list_by_filter(first_element_filter)
        second_element_list = reliase.get_elements_list_by_filter(second_element_filter)

        self.ui.experimentsTab.setRowCount(0)
        self.ui.experimentsTab.setSelectionBehavior(QAbstractItemView.SelectRows) #  при нажатии на таблицу выделяется не ячейка, а выбранная строка целиком

        self.setStyleSheet("""
                    QTableWidget::item:selected{
                        background-color: #F0FFF0;
                        color: #000000;
                    }
                    """)

        experiments = get_all_elements('experiments')

        j = 0
        for i in range(0, len(experiments)):
            if (experiments[i]['first_element'] in first_element_list or first_element_filter == 'Any') and (experiments[i]['second_element'] in second_element_list or second_element_filter == 'Any'):
                self.ui.experimentsTab.insertRow(self.ui.experimentsTab.rowCount())
                exp_arr = json.loads(experiments[i]['source_data'])
                self.ui.experimentsTab.setItem(j, 0, QTableWidgetItem(str(experiments[i]['id'])))
                self.ui.experimentsTab.setItem(j, 1, QTableWidgetItem(experiments[i]['first_element']))
                self.ui.experimentsTab.setItem(j, 2, QTableWidgetItem(experiments[i]['second_element']))
                temperature = lambda: 'Not const' if str(experiments[i]['temperature']) == 'None' else str(experiments[i]['temperature'])
                pressure = lambda: 'Not const' if str(experiments[i]['pressure']) == 'None' else str(experiments[i]['pressure'])
                self.ui.experimentsTab.setItem(j, 3, QTableWidgetItem(temperature()))
                self.ui.experimentsTab.setItem(j, 4, QTableWidgetItem(pressure()))
                self.ui.experimentsTab.setItem(j, 5, QTableWidgetItem(reliase.get_article_name(experiments[i]['article'])))
                j += 1
    

        # подгон размера столбцов под данные
        horizontalHeader = self.ui.experimentsTab.horizontalHeader()
        for i in range(self.ui.experimentsTab.columnCount() - 1):
            horizontalHeader.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        horizontalHeader.setSectionResizeMode(self.ui.experimentsTab.columnCount() - 1, QtWidgets.QHeaderView.Stretch)

    # обновление таблицы элементов
    def update_table_experiments(self):
        self.create_table_experiments()

    # создание таблицы элементов
    def create_table_elements(self):
        self.ui.elementsTab.setRowCount(0)
        self.ui.elementsTab.setRowCount(1)

        elements = get_all_elements('elements')
        
        for i in range(0, len(elements)):
            self.ui.elementsTab.insertRow(self.ui.elementsTab.rowCount())
            spec_arr = elements[i]['branch'].split(';')
            self.ui.elementsTab.setItem(i, 0, QTableWidgetItem(elements[i]['name']))
            self.ui.elementsTab.setItem(i, 1, QTableWidgetItem(crash(spec_arr)))

    # обработка нажатия на таблицу экспериментов
    def clicked_on_experiments_tab(self, event = None):
        if self.current_row != self.ui.experimentsTab.currentRow():
            self.current_row = self.ui.experimentsTab.currentRow()
        else:
            if event:
                self.ui.experimentsTab.clearSelection()
                self.ui.experimentsTab.setCurrentCell(-1, 0)
                self.current_row = -1


    # функция для обработки нажатия на кнопку "Добавить" во вкладке Эксперименты
    def add_button_clicked(self):
        add_window = ImportExperimentDialog()
        add_window.exec()


    # вывод информации об статьях
    def show_articles(self):
        items = get_all_elements('articles')
        for item in items:
            item_string = 'Имя: ' +  item['name'] + '\n' + 'Автор: ' + item['author'] + '\n' + 'Год издания: ' + str(item['year'])
            self.articles_list.addItem(item_string)
            self.articles_list.addItem(item['link'])
            self.articles_list.addItem('')

    def contextMenuEvent(self, event):
        try:
            top_row = self.ui.experimentsTab.selectionModel().selectedRows()
            rows = [i for i in range(self.ui.experimentsTab.currentRow() - len(self.ui.experimentsTab.selectionModel().selectedRows()) + 1, self.ui.experimentsTab.currentRow() + 1)]
            id_exp = [int(self.ui.experimentsTab.item(row, 0).text()) for row in rows]
            id_exp_string = ''
            for i in id_exp:
                id_exp_string += f'{i},'
            id_exp_string = id_exp_string[:-1]

            item = self.ui.experimentsTab.itemAt(event.pos())
            #now_current_row = self.ui.experimentsTab.currentRow()
            self.clicked_on_experiments_tab()
            if self.ui.tabWidget.currentIndex() == 1 and self.current_row != -1:
                contextMenu = QMenu(self)
                calcAct = contextMenu.addAction("Рассчитать")
                showAct = contextMenu.addAction("Информация")
                action = contextMenu.exec_(self.mapToGlobal(event.pos()))
                if action == calcAct:
                    self.ui.tabWidget.setCurrentIndex(4)
                    self.ui.id_exp_edit.setText(id_exp_string)
                elif action == showAct:
                    d = ExperimentInfoDialog(id_exp)
                    d.exec()
        except Exception as ex:
            print(ex)


    def makeCalculatePage(self):
        self.ui.calculateButton.clicked.connect(self.calculateButton_clicked)
        self.ui.methodsComboBox.addItem('Имитации отжига')
        self.ui.methodsComboBox.addItem('Гаусса-Зейделя')
        self.ui.methodsComboBox.addItem('Хукка-Дживса')
        self.ui.methodsComboBox.addItem('Антиградиент')
        self.ui.methodsComboBox.addItem('Ньютона')

        self.methods_dict = {'Имитации отжига': 0, 'Гаусса-Зейделя': 1, 'Хукка-Дживса': 2, 'Антиградиент': 3, 'Ньютона': 4}
        self.method_name = 'Имитации отжига'

        self.model = functions.margulis

        self.ui.methodsComboBox.activated.connect(self.updateMethodsComboBox)
        self.attemptsTabWidget.tabCloseRequested.connect(self.close_attempt_tab)

        self.ui.attemptsTabWidget.removeTab(0)
        self.ui.attemptsTabWidget.removeTab(0)

        self.ui.multistartCheckBox.stateChanged.connect(self.multistartCheckBoxChanged)
        self.turn_visibility(visibility=True)

    def turn_visibility(self, visibility: bool = True):
        self.ui.label_9.setEnabled(visibility)
        self.ui.label_10.setEnabled(visibility)
        self.ui.A12_init_edit.setEnabled(visibility)
        self.ui.A21_init_edit.setEnabled(visibility)
        self.ui.label.setEnabled(not visibility)
        self.ui.label_7.setEnabled(not visibility)
        self.ui.label_11.setEnabled(not visibility)
        self.ui.label_8.setEnabled(not visibility)
        self.ui.label_14.setEnabled(not visibility)
        self.ui.A12_min_edit.setEnabled(not visibility)
        self.ui.A12_max_edit.setEnabled(not visibility)
        self.ui.A21_min_edit.setEnabled(not visibility)
        self.ui.A21_max_edit.setEnabled(not visibility)
        self.ui.count_edit.setEnabled(not visibility)

    def multistartCheckBoxChanged(self):
        if self.ui.multistartCheckBox.isChecked():
            self.turn_visibility(visibility=False)
        else:
            self.turn_visibility(visibility=True)

    def updateMethodsComboBox(self):
        self.method_name = self.ui.methodsComboBox.currentText()

    # функция для проверки корректности ввода данных пользователем
    def checking_experiments_number_input(self):
        id_experiments = self.ui.id_exp_edit.text()
        for i in id_experiments:
            if i not in '0123456789, ':
                return False
        return True

    def checking_input(self):
        if self.ui.multistartCheckBox.isChecked():
            return (self.ui.A12_min_edit.text().isdigit() and self.ui.A12_max_edit.text().isdigit() and
                    self.ui.A21_min_edit.text().isdigit() and self.ui.A21_max_edit.text().isdigit() and
                    self.ui.count_edit.text().isdigit() and self.checking_experiments_number_input())
        return self.ui.A12_init_edit.text().isdigit() and self.ui.A21_init_edit.text().isdigit() and self.checking_experiments_number_input()

    # функция вызова предупреждения об ошибке в случае некорректного ввода
    @staticmethod
    def error_message():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка ввода")
        msg.setInformativeText('Некорректный ввод')
        msg.setWindowTitle("Сообщение об ошибке")
        msg.exec_()

    def calculateButton_clicked(self):
        try:
            if self.checking_input():
                id_experiments = self.ui.id_exp_edit.text()
                id_experiments.replace(' ', '')
                for id_experiment in id_experiments.split(','):
                    id_exp = int(id_experiment)

                    if self.ui.multistartCheckBox.isChecked():
                        a12_min = float(self.ui.A12_min_edit.text())
                        a12_max = float(self.ui.A12_max_edit.text())
                        a21_min = float(self.ui.A21_min_edit.text())
                        a21_max = float(self.ui.A21_max_edit.text())
                        count = int(self.ui.count_edit.text())
                        result = multi_start(id_exp, a12_min, a12_max, a21_min, a21_max, count, self.methods_dict[self.method_name], self.model)
                        attempt = Attempt(id_exp, self.model, self.methods_dict[self.method_name],
                                          {'a12_min': a12_min, 'a12_max': a12_max, 'a21_min': a21_min, 'a21_max': a21_max}, {'result': result})
                    else:
                        a12 = float(self.ui.A12_init_edit.text())
                        a21 = float(self.ui.A21_init_edit.text())
                        a12_new, a21_new = simple_calculation(id_exp, a12, a21, self.methods_dict[self.method_name], self.model)
                        attempt = Attempt(id_exp, self.model, self.methods_dict[self.method_name], {'a12': a12, 'a21': a21}, {'a12': a12_new, 'a21': a21_new})
                    page = AttemptWidget(attempt)
                    n = attempt.number
                    self.ui.attemptsTabWidget.addTab(page, f'Attempt {n}')
                    self.ui.attemptsTabWidget.setCurrentIndex(self.ui.attemptsTabWidget.count() - 1)
            else:
                self.error_message()
        except Exception as ex:
            print(ex)

    def close_attempt_tab(self, index):
        self.attemptsTabWidget.removeTab(index)


    def filterButton_clicked(self):
        first_element_filter = self.ui.firstElementEdit.text()
        second_element_filter = self.ui.secondElementEdit.text()
        self.create_table_experiments(first_element_filter=first_element_filter, second_element_filter=second_element_filter)

    def swapButtonClicked(self):
        first_element = self.ui.firstElementEdit.text()
        second_element = self.ui.secondElementEdit.text()
        self.ui.firstElementEdit.setText(second_element)
        self.ui.secondElementEdit.setText(first_element)


##################################################################################################################################################################




if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()



# Hvwg wg bch hvs sbr, hvwg wg xigh hvs psuwbbwbu. Юноьантъ.