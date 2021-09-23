from PyQt5 import QtWidgets
import Interface.MainWindow as Design_MainWin
from os.path import exists
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import shutil




class Main_Frame(QtWidgets.QMainWindow, Design_MainWin.Ui_MainWindow):
    '''Класс главного окна'''

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле MainWindow.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.File_input_button.clicked.connect(self.browse_file_input)    #Привязка к кнопке функции поиска входного файла
        self.File_output_button.clicked.connect(self.browse_file_output)  #Привязка к кнопке функции указания директории для выходного файла
        self.Calculate_button.clicked.connect(self.Calculate)             #Привязка к кнопке функции, начинающей весь рассчёт

    #-----------------------------------------------------------------------

    #Функция для ручного поиска входного файла по проводнику
    def browse_file_input(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл")  #Открывается окно поиска по "проводнику"
        if file:             #Если файл был выбран
            file = file[0]   #Берём путь до файла
            self.File_url_input.setText(file)  #Вставляем путь в поле ввода

    # -----------------------------------------------------------------------

    #Функция для ручного указания директории для выходного файла
    def browse_file_output(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory()  #Открывается окно поиска по "проводнику"
        if directory:
            directory_path = ''
            for char in directory:
                directory_path += char                    #Берём путь до директории
            self.File_url_output.setText(directory)     #И помещаем в поле для ввода

    # -----------------------------------------------------------------------

    #Вывод ошибки в область ошибок
    def Show_error(self, error_str):
        self.Finish_label.setText('Возникли проблемы!')  # Меняем статус
        self.Finish_label.setStyleSheet('color: #ff0000')  # и его цвет
        self.Problems_text.setPlainText(error_str)

    # -----------------------------------------------------------------------

    #Функция, запускающая алгоритм расчёта
    def Calculate(self):
        IN = self.File_url_input.toPlainText()                        #Берём путь до файла из текствого поля
        OUT = self.File_url_output.toPlainText()  # Берём путь до директории выходного файла
        OUT += '/' + self.Edit_filename_output.toPlainText() + '.txt'  # Добавляем имя файла к пути сохранения


        #Если входной файл, указанный пользователем, существует
        if exists(IN):
            self.Finish_label.setText('Обрабатываю аудиоданные...')
            #ЗАПУСКАЕМ АЛГОРИТМ РАСЧЁТА
            error_str = self.Hear_and_write(IN, OUT)
        else:
            error_str = "Некорректно указан путь до входного файла."

        #Если проблем не возникло
        if(error_str == True):
            self.Finish_label.setStyleSheet('color: rgb(0, 170, 0);')
            self.Finish_label.setText('Готово!')  # По выполнении уведомляем пользователя надписью ниже главной кнопки

        #Если же проблемы всё-таки возникли
        elif (type(' ') == type('error_str')):
            self.Show_error(error_str)

    # -----------------------------------------------------------------------

    #Основная функция, обрабатывающая аудиофайл и выводящая текст.
    def Hear_and_write(self, IN, OUT):
        # a function that splits the audio file into chunks
        # and applies speech recognition
        path = IN
        # open the audio file stored in
        # the local system as a wav file.
        song = AudioSegment.from_wav(path)

        # open a file where we will concatenate
        # and store the recognized text
        fh = open(OUT, "w+")

        # split track where silence is 0.5 seconds
        # or more and get chunks
        chunks = split_on_silence(song,
                                  # must be silent for at least 0.5 seconds
                                  # or 500 ms. adjust this value based on user
                                  # requirement. if the speaker stays silent for
                                  # longer, increase this value. else, decrease it.
                                  min_silence_len=1000,

                                  # consider it silent if quieter than -16 dBFS
                                  # adjust this per requirement
                                  silence_thresh=-30
                                  )

        # create a directory to store the audio chunks.
        try:
            os.mkdir('audio_chunks')
        except(FileExistsError):
            pass

        # move into the directory to
        # store the audio files.
        os.chdir('audio_chunks')

        log_str = ''
        i = 0
        # process each chunk
        for chunk in chunks:

            # Create 0.5 seconds silence chunk
            chunk_silent = AudioSegment.silent(duration=10)

            # add 0.5 sec silence to beginning and
            # end of audio chunk. This is done so that
            # it doesn't seem abruptly sliced.
            audio_chunk = chunk_silent + chunk + chunk_silent

            # export audio chunk and save it in
            # the current directory.
            print("saving chunk{0}.wav".format(i))
            # specify the bitrate to be 192 k
            audio_chunk.export("./chunk{0}.wav".format(i), bitrate='192k', format="wav")

            # the name of the newly created chunk
            filename = 'chunk' + str(i) + '.wav'

            log_str += "Обработка фрагмента " + str(i) + '\n'
            self.Problems_text.setPlainText(log_str)

            # get the name of the newly created chunk
            # in the AUDIO_FILE variable for later use.
            file = filename

            # create a speech recognition object
            r = sr.Recognizer()

            # recognize the chunk
            with sr.AudioFile(file) as source:
                # remove this if it is not working
                # correctly.
                # r.adjust_for_ambient_noise(source)
                audio_listened = r.listen(source)

            try:
                # try converting it to text
                rec = r.recognize_google(audio_listened, language="ru-RU")
                # write the output to the file.
                fh.write(rec + ". ")

                # catch any errors.
            except sr.UnknownValueError:
                log_str += 'Аудиофрагмент ' + str(i) + ': ' + 'Не получилось распознать аудио.\n\n'
                self.Problems_text.setPlainText(log_str)


            except sr.RequestError as e:
                print("Could not request results. check your internet connection")
                error_str = 'Не удалось получить результат. Пожалуйста, проверьте своё Интернет соединение.'
                mkpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'audio_chunks')
                shutil.rmtree(mkpath)

                return error_str


            i += 1

        os.chdir('..')
        mkpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'audio_chunks')
        shutil.rmtree(mkpath)

        return True