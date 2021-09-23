import sys
from MainWin_GUI import *


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Main_Frame()  # Создаём объект класса Main_Frame
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

main()