import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction, QTabWidget, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout, QComboBox, QSpinBox, QTextEdit, QDateTimeEdit
)
from PyQt5.QtCore import QDateTime
import psycopg2
import os


# Настройки подключения к базе данных
DB_HOST = 'localhost'
DB_NAME = 'Booking_db'
DB_USER = 'postgres'
DB_PASS = 'НЕ СКАЖУ ПАРОЛЬ'

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # USERS
    def fetch_users(self, search=None):
        conn = self.connect()
        with conn.cursor() as cur:
            if search:
                query = """
                    SELECT user_id, first_name, last_name, email, role FROM Users
                    WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR role ILIKE %s
                    ORDER BY user_id
                """
                like = f"%{search}%"
                cur.execute(query, (like, like, like, like))
            else:
                cur.execute("SELECT user_id, first_name, last_name, email, role FROM Users ORDER BY user_id")
            return cur.fetchall()

    def add_user(self, first_name, last_name, email, role):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Users (first_name, last_name, email, role) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, role)
            )
        conn.commit()

    def update_user(self, user_id, first_name, last_name, email, role):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Users SET first_name=%s, last_name=%s, email=%s, role=%s WHERE user_id=%s",
                (first_name, last_name, email, role, user_id)
            )
        conn.commit()

    def delete_user(self, user_id):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Users WHERE user_id=%s", (user_id,))
        conn.commit()

    # ROOM TYPES
    def fetch_room_types(self):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT type_id, type_name FROM RoomTypes ORDER BY type_id")
            return cur.fetchall()

    def fetch_room_types_full(self):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT type_id, type_name, description FROM RoomTypes ORDER BY type_id")
            return cur.fetchall()

    def add_room_type(self, type_name, description):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO RoomTypes (type_name, description) VALUES (%s, %s)", (type_name, description))
        conn.commit()

    def update_room_type(self, type_id, type_name, description):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE RoomTypes SET type_name=%s, description=%s WHERE type_id=%s", (type_name, description, type_id))
        conn.commit()

    def delete_room_type(self, type_id):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM RoomTypes WHERE type_id=%s", (type_id,))
        conn.commit()

    # ROOMS
    def fetch_rooms(self, search=None):
        conn = self.connect()
        with conn.cursor() as cur:
            if search:
                query = """
                    SELECT r.room_id, r.room_number, r.capacity, t.type_name, r.is_available
                    FROM Rooms r LEFT JOIN RoomTypes t ON r.type_id = t.type_id
                    WHERE r.room_number ILIKE %s OR t.type_name ILIKE %s
                    ORDER BY r.room_id
                """
                like = f"%{search}%"
                cur.execute(query, (like, like))
            else:
                cur.execute("""
                    SELECT r.room_id, r.room_number, r.capacity, t.type_name, r.is_available
                    FROM Rooms r LEFT JOIN RoomTypes t ON r.type_id = t.type_id
                    ORDER BY r.room_id
                """)
            return cur.fetchall()

    def add_room(self, room_number, capacity, type_id, is_available):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Rooms (room_number, capacity, type_id, is_available) VALUES (%s, %s, %s, %s)",
                (room_number, capacity, type_id, is_available)
            )
        conn.commit()

    def update_room(self, room_id, room_number, capacity, type_id, is_available):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Rooms SET room_number=%s, capacity=%s, type_id=%s, is_available=%s WHERE room_id=%s",
                (room_number, capacity, type_id, is_available, room_id)
            )
        conn.commit()

    def delete_room(self, room_id):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Rooms WHERE room_id=%s", (room_id,))
        conn.commit()

    # RESERVATIONS
    def fetch_reservations(self, search=None):
        conn = self.connect()
        with conn.cursor() as cur:
            if search:
                query = """
                    SELECT res.reservation_id, r.room_number, u.first_name || ' ' || u.last_name, res.start_time, res.end_time, res.purpose
                    FROM Reservations res
                    LEFT JOIN Rooms r ON res.room_id = r.room_id
                    LEFT JOIN Users u ON res.user_id = u.user_id
                    WHERE r.room_number ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s OR res.purpose ILIKE %s
                    ORDER BY res.reservation_id
                """
                like = f"%{search}%"
                cur.execute(query, (like, like, like, like))
            else:
                cur.execute("""
                    SELECT res.reservation_id, r.room_number, u.first_name || ' ' || u.last_name, res.start_time, res.end_time, res.purpose
                    FROM Reservations res
                    LEFT JOIN Rooms r ON res.room_id = r.room_id
                    LEFT JOIN Users u ON res.user_id = u.user_id
                    ORDER BY res.reservation_id
                """)
            return cur.fetchall()

    def add_reservation(self, room_id, user_id, start_time, end_time, purpose):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Reservations (room_id, user_id, start_time, end_time, purpose) VALUES (%s, %s, %s, %s, %s)",
                (room_id, user_id, start_time, end_time, purpose)
            )
        conn.commit()

    def update_reservation(self, reservation_id, room_id, user_id, start_time, end_time, purpose):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Reservations SET room_id=%s, user_id=%s, start_time=%s, end_time=%s, purpose=%s WHERE reservation_id=%s",
                (room_id, user_id, start_time, end_time, purpose, reservation_id)
            )
        conn.commit()

    def delete_reservation(self, reservation_id):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Reservations WHERE reservation_id=%s", (reservation_id,))
        conn.commit()

    # SCHEDULES
    def fetch_schedules(self, search=None):
        conn = self.connect()
        with conn.cursor() as cur:
            if search:
                query = """
                    SELECT s.schedule_id, r.room_number, s.event_name, s.start_time, s.end_time
                    FROM Schedules s
                    LEFT JOIN Rooms r ON s.room_id = r.room_id
                    WHERE r.room_number ILIKE %s OR s.event_name ILIKE %s
                    ORDER BY s.schedule_id
                """
                like = f"%{search}%"
                cur.execute(query, (like, like))
            else:
                cur.execute("""
                    SELECT s.schedule_id, r.room_number, s.event_name, s.start_time, s.end_time
                    FROM Schedules s
                    LEFT JOIN Rooms r ON s.room_id = r.room_id
                    ORDER BY s.schedule_id
                """)
            return cur.fetchall()

    def add_schedule(self, room_id, event_name, start_time, end_time):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Schedules (room_id, event_name, start_time, end_time) VALUES (%s, %s, %s, %s)",
                (room_id, event_name, start_time, end_time)
            )
        conn.commit()

    def update_schedule(self, schedule_id, room_id, event_name, start_time, end_time):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Schedules SET room_id=%s, event_name=%s, start_time=%s, end_time=%s WHERE schedule_id=%s",
                (room_id, event_name, start_time, end_time, schedule_id)
            )
        conn.commit()

    def delete_schedule(self, schedule_id):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Schedules WHERE schedule_id=%s", (schedule_id,))
        conn.commit()

# --- Диалоги ---
class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setWindowTitle('Пользователь')
        self.layout = QFormLayout(self)
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(['student', 'teacher', 'admin', 'staff'])
        self.layout.addRow('Имя:', self.first_name)
        self.layout.addRow('Фамилия:', self.last_name)
        self.layout.addRow('Email:', self.email)
        self.layout.addRow('Роль:', self.role)
        self.btns = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('Отмена')
        self.btns.addWidget(self.ok_btn)
        self.btns.addWidget(self.cancel_btn)
        self.layout.addRow(self.btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        if user:
            self.first_name.setText(user[1])
            self.last_name.setText(user[2])
            self.email.setText(user[3])
            idx = self.role.findText(user[4])
            if idx >= 0:
                self.role.setCurrentIndex(idx)
    def get_data(self):
        return (
            self.first_name.text(),
            self.last_name.text(),
            self.email.text(),
            self.role.currentText()
        )

class RoomDialog(QDialog):
    def __init__(self, parent=None, room=None, room_types=None):
        super().__init__(parent)
        self.setWindowTitle('Комната')
        self.layout = QFormLayout(self)
        self.room_number = QLineEdit()
        self.capacity = QSpinBox()
        self.capacity.setMinimum(1)
        self.type_box = QComboBox()
        self.type_map = {}
        if room_types:
            for tid, tname in room_types:
                self.type_box.addItem(tname, tid)
                self.type_map[tname] = tid
        self.is_available = QComboBox()
        self.is_available.addItems(['Да', 'Нет'])
        self.layout.addRow('Номер:', self.room_number)
        self.layout.addRow('Вместимость:', self.capacity)
        self.layout.addRow('Тип:', self.type_box)
        self.layout.addRow('Доступна:', self.is_available)
        self.btns = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('Отмена')
        self.btns.addWidget(self.ok_btn)
        self.btns.addWidget(self.cancel_btn)
        self.layout.addRow(self.btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        if room:
            self.room_number.setText(room[1])
            self.capacity.setValue(int(room[2]))
            idx = self.type_box.findText(room[3])
            if idx >= 0:
                self.type_box.setCurrentIndex(idx)
            self.is_available.setCurrentIndex(0 if room[4] == 'True' or room[4] == True else 1)
    def get_data(self):
        return (
            self.room_number.text(),
            self.capacity.value(),
            self.type_box.currentData(),
            self.is_available.currentIndex() == 0
        )

class ReservationDialog(QDialog):
    def __init__(self, parent=None, reservation=None, rooms=None, users=None):
        super().__init__(parent)
        self.setWindowTitle('Бронирование')
        self.layout = QFormLayout(self)
        self.room_box = QComboBox()
        self.room_map = {}
        if rooms:
            for rid, rnum in rooms:
                self.room_box.addItem(rnum, rid)
                self.room_map[rnum] = rid
        self.user_box = QComboBox()
        self.user_map = {}
        if users:
            for uid, uname in users:
                self.user_box.addItem(uname, uid)
                self.user_map[uname] = uid
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time.setCalendarPopup(True)
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_time.setCalendarPopup(True)
        self.purpose = QTextEdit()
        self.layout.addRow('Комната:', self.room_box)
        self.layout.addRow('Пользователь:', self.user_box)
        self.layout.addRow('Начало:', self.start_time)
        self.layout.addRow('Конец:', self.end_time)
        self.layout.addRow('Цель:', self.purpose)
        self.btns = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('Отмена')
        self.btns.addWidget(self.ok_btn)
        self.btns.addWidget(self.cancel_btn)
        self.layout.addRow(self.btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        if reservation:
            self.room_box.setCurrentText(reservation[1])
            self.user_box.setCurrentText(reservation[2])
            self.start_time.setDateTime(QDateTime.fromString(str(reservation[3]), 'yyyy-MM-dd HH:mm:ss'))
            self.end_time.setDateTime(QDateTime.fromString(str(reservation[4]), 'yyyy-MM-dd HH:mm:ss'))
            self.purpose.setPlainText(reservation[5])
    def get_data(self):
        return (
            self.room_box.currentData(),
            self.user_box.currentData(),
            self.start_time.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
            self.end_time.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
            self.purpose.toPlainText()
        )

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None, rooms=None):
        super().__init__(parent)
        self.setWindowTitle('Расписание')
        self.layout = QFormLayout(self)
        self.room_box = QComboBox()
        self.room_map = {}
        if rooms:
            for rid, rnum in rooms:
                self.room_box.addItem(rnum, rid)
                self.room_map[rnum] = rid
        self.event_name = QLineEdit()
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time.setCalendarPopup(True)
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_time.setCalendarPopup(True)
        self.layout.addRow('Комната:', self.room_box)
        self.layout.addRow('Событие:', self.event_name)
        self.layout.addRow('Начало:', self.start_time)
        self.layout.addRow('Конец:', self.end_time)
        self.btns = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('Отмена')
        self.btns.addWidget(self.ok_btn)
        self.btns.addWidget(self.cancel_btn)
        self.layout.addRow(self.btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        if schedule:
            self.room_box.setCurrentText(schedule[1])
            self.event_name.setText(schedule[2])
            self.start_time.setDateTime(QDateTime.fromString(str(schedule[3]), 'yyyy-MM-dd HH:mm:ss'))
            self.end_time.setDateTime(QDateTime.fromString(str(schedule[4]), 'yyyy-MM-dd HH:mm:ss'))
    def get_data(self):
        return (
            self.room_box.currentData(),
            self.event_name.text(),
            self.start_time.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
            self.end_time.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        )

class RoomTypeDialog(QDialog):
    def __init__(self, parent=None, room_type=None):
        super().__init__(parent)
        self.setWindowTitle('Тип комнаты')
        self.layout = QFormLayout(self)
        self.type_name = QLineEdit()
        self.description = QTextEdit()
        self.layout.addRow('Название:', self.type_name)
        self.layout.addRow('Описание:', self.description)
        self.btns = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.cancel_btn = QPushButton('Отмена')
        self.btns.addWidget(self.ok_btn)
        self.btns.addWidget(self.cancel_btn)
        self.layout.addRow(self.btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        if room_type:
            self.type_name.setText(room_type[1])
            self.description.setPlainText(room_type[2] if room_type[2] else '')
    def get_data(self):
        return (
            self.type_name.text(),
            self.description.toPlainText()
        )

# --- Вкладки ---
class UsersTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Поиск по имени, фамилии, email, роли...')
        self.search_btn = QPushButton('Поиск')
        self.reset_btn = QPushButton('Сбросить')
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.search_layout)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Добавить')
        self.edit_btn = QPushButton('Изменить')
        self.del_btn = QPushButton('Удалить')
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.del_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_user)
        self.edit_btn.clicked.connect(self.edit_user)
        self.del_btn.clicked.connect(self.delete_user)
        self.search_btn.clicked.connect(self.search_users)
        self.reset_btn.clicked.connect(self.load_users)
        self.load_users()

    def load_users(self):
        users = self.db.fetch_users()
        self.show_users(users)

    def show_users(self, users):
        headers = ['ID', 'Имя', 'Фамилия', 'Email', 'Роль']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(users))
        for row_idx, row_data in enumerate(users):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def search_users(self):
        text = self.search_edit.text().strip()
        users = self.db.fetch_users(search=text) if text else self.db.fetch_users()
        self.show_users(users)

    def add_user(self):
        dlg = UserDialog(self)
        if dlg.exec_():
            first_name, last_name, email, role = dlg.get_data()
            try:
                self.db.add_user(first_name, last_name, email, role)
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить пользователя:\n{e}')

    def edit_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите пользователя для редактирования')
            return
        user = [self.table.item(row, i).text() for i in range(5)]
        dlg = UserDialog(self, user)
        if dlg.exec_():
            first_name, last_name, email, role = dlg.get_data()
            try:
                self.db.update_user(user[0], first_name, last_name, email, role)
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить пользователя:\n{e}')

    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите пользователя для удаления')
            return
        user_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Удалить', 'Удалить выбранного пользователя?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_user(user_id)
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить пользователя:\n{e}')

class RoomsTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Поиск по номеру или типу...')
        self.search_btn = QPushButton('Поиск')
        self.reset_btn = QPushButton('Сбросить')
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.search_layout)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Добавить')
        self.edit_btn = QPushButton('Изменить')
        self.del_btn = QPushButton('Удалить')
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.del_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_room)
        self.edit_btn.clicked.connect(self.edit_room)
        self.del_btn.clicked.connect(self.delete_room)
        self.search_btn.clicked.connect(self.search_rooms)
        self.reset_btn.clicked.connect(self.load_rooms)
        self.load_rooms()

    def load_rooms(self):
        rooms = self.db.fetch_rooms()
        self.show_rooms(rooms)

    def show_rooms(self, rooms):
        headers = ['ID', 'Номер', 'Вместимость', 'Тип', 'Доступна']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rooms))
        for row_idx, row_data in enumerate(rooms):
            for col_idx, value in enumerate(row_data):
                if col_idx == 4:
                    value = 'Да' if value else 'Нет'
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def search_rooms(self):
        text = self.search_edit.text().strip()
        rooms = self.db.fetch_rooms(search=text) if text else self.db.fetch_rooms()
        self.show_rooms(rooms)

    def add_room(self):
        room_types = self.db.fetch_room_types()
        dlg = RoomDialog(self, room_types=room_types)
        if dlg.exec_():
            room_number, capacity, type_id, is_available = dlg.get_data()
            try:
                self.db.add_room(room_number, capacity, type_id, is_available)
                self.load_rooms()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить комнату:\n{e}')

    def edit_room(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите комнату для редактирования')
            return
        room = [self.table.item(row, i).text() for i in range(5)]
        room_types = self.db.fetch_room_types()
        dlg = RoomDialog(self, room=room, room_types=room_types)
        if dlg.exec_():
            room_number, capacity, type_id, is_available = dlg.get_data()
            try:
                self.db.update_room(room[0], room_number, capacity, type_id, is_available)
                self.load_rooms()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить комнату:\n{e}')

    def delete_room(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите комнату для удаления')
            return
        room_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Удалить', 'Удалить выбранную комнату?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_room(room_id)
                self.load_rooms()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить комнату:\n{e}')

class RoomTypesTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Добавить')
        self.edit_btn = QPushButton('Изменить')
        self.del_btn = QPushButton('Удалить')
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.del_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_type)
        self.edit_btn.clicked.connect(self.edit_type)
        self.del_btn.clicked.connect(self.delete_type)
        self.load_types()

    def load_types(self):
        types = self.db.fetch_room_types_full()
        headers = ['ID', 'Название', 'Описание']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(types))
        for row_idx, row_data in enumerate(types):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def add_type(self):
        dlg = RoomTypeDialog(self)
        if dlg.exec_():
            type_name, description = dlg.get_data()
            try:
                self.db.add_room_type(type_name, description)
                self.load_types()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить тип комнаты:\n{e}')

    def edit_type(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите тип для редактирования')
            return
        room_type = [self.table.item(row, i).text() for i in range(3)]
        dlg = RoomTypeDialog(self, room_type)
        if dlg.exec_():
            type_name, description = dlg.get_data()
            try:
                self.db.update_room_type(room_type[0], type_name, description)
                self.load_types()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить тип комнаты:\n{e}')

    def delete_type(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите тип для удаления')
            return
        type_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Удалить', 'Удалить выбранный тип комнаты?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_room_type(type_id)
                self.load_types()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить тип комнаты:\n{e}')

class ReservationsTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Поиск по комнате, пользователю, цели...')
        self.search_btn = QPushButton('Поиск')
        self.reset_btn = QPushButton('Сбросить')
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.search_layout)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Добавить')
        self.edit_btn = QPushButton('Изменить')
        self.del_btn = QPushButton('Удалить')
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.del_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_reservation)
        self.edit_btn.clicked.connect(self.edit_reservation)
        self.del_btn.clicked.connect(self.delete_reservation)
        self.search_btn.clicked.connect(self.search_reservations)
        self.reset_btn.clicked.connect(self.load_reservations)
        self.load_reservations()

    def load_reservations(self):
        reservations = self.db.fetch_reservations()
        self.show_reservations(reservations)

    def show_reservations(self, reservations):
        headers = ['ID', 'Комната', 'Пользователь', 'Начало', 'Конец', 'Цель']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(reservations))
        for row_idx, row_data in enumerate(reservations):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def search_reservations(self):
        text = self.search_edit.text().strip()
        reservations = self.db.fetch_reservations(search=text) if text else self.db.fetch_reservations()
        self.show_reservations(reservations)

    def add_reservation(self):
        rooms = [(r[0], r[1]) for r in self.db.fetch_rooms()]
        users = [(u[0], f"{u[1]} {u[2]}") for u in self.db.fetch_users()]
        dlg = ReservationDialog(self, rooms=rooms, users=users)
        if dlg.exec_():
            room_id, user_id, start_time, end_time, purpose = dlg.get_data()
            try:
                self.db.add_reservation(room_id, user_id, start_time, end_time, purpose)
                self.load_reservations()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить бронирование:\n{e}')

    def edit_reservation(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите бронирование для редактирования')
            return
        reservation = [self.table.item(row, i).text() for i in range(6)]
        rooms = [(r[0], r[1]) for r in self.db.fetch_rooms()]
        users = [(u[0], f"{u[1]} {u[2]}") for u in self.db.fetch_users()]
        dlg = ReservationDialog(self, reservation=reservation, rooms=rooms, users=users)
        if dlg.exec_():
            room_id, user_id, start_time, end_time, purpose = dlg.get_data()
            try:
                self.db.update_reservation(reservation[0], room_id, user_id, start_time, end_time, purpose)
                self.load_reservations()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить бронирование:\n{e}')

    def delete_reservation(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите бронирование для удаления')
            return
        reservation_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Удалить', 'Удалить выбранное бронирование?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_reservation(reservation_id)
                self.load_reservations()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить бронирование:\n{e}')

class SchedulesTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Поиск по комнате или событию...')
        self.search_btn = QPushButton('Поиск')
        self.reset_btn = QPushButton('Сбросить')
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.reset_btn)
        self.layout.addLayout(self.search_layout)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Добавить')
        self.edit_btn = QPushButton('Изменить')
        self.del_btn = QPushButton('Удалить')
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.del_btn)
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_schedule)
        self.edit_btn.clicked.connect(self.edit_schedule)
        self.del_btn.clicked.connect(self.delete_schedule)
        self.search_btn.clicked.connect(self.search_schedules)
        self.reset_btn.clicked.connect(self.load_schedules)
        self.load_schedules()

    def load_schedules(self):
        schedules = self.db.fetch_schedules()
        self.show_schedules(schedules)

    def show_schedules(self, schedules):
        headers = ['ID', 'Комната', 'Событие', 'Начало', 'Конец']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(schedules))
        for row_idx, row_data in enumerate(schedules):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def search_schedules(self):
        text = self.search_edit.text().strip()
        schedules = self.db.fetch_schedules(search=text) if text else self.db.fetch_schedules()
        self.show_schedules(schedules)

    def add_schedule(self):
        rooms = [(r[0], r[1]) for r in self.db.fetch_rooms()]
        dlg = ScheduleDialog(self, rooms=rooms)
        if dlg.exec_():
            room_id, event_name, start_time, end_time = dlg.get_data()
            try:
                self.db.add_schedule(room_id, event_name, start_time, end_time)
                self.load_schedules()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить расписание:\n{e}')

    def edit_schedule(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите расписание для редактирования')
            return
        schedule = [self.table.item(row, i).text() for i in range(5)]
        rooms = [(r[0], r[1]) for r in self.db.fetch_rooms()]
        dlg = ScheduleDialog(self, schedule=schedule, rooms=rooms)
        if dlg.exec_():
            room_id, event_name, start_time, end_time = dlg.get_data()
            try:
                self.db.update_schedule(schedule[0], room_id, event_name, start_time, end_time)
                self.load_schedules()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить расписание:\n{e}')

    def delete_schedule(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите расписание для удаления')
            return
        schedule_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Удалить', 'Удалить выбранное расписание?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_schedule(schedule_id)
                self.load_schedules()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить расписание:\n{e}')

# --- Главное окно ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Booking App')
        self.setGeometry(100, 100, 1000, 700)
        self.db = Database()
        self.init_ui()
        self.check_db_connection()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(UsersTab(self.db), 'Пользователи')
        self.tabs.addTab(RoomsTab(self.db), 'Комнаты')
        self.tabs.addTab(RoomTypesTab(self.db), 'Типы комнат')
        self.tabs.addTab(ReservationsTab(self.db), 'Бронирования')
        self.tabs.addTab(SchedulesTab(self.db), 'Расписания')
        self.setCentralWidget(self.tabs)

    def check_db_connection(self):
        try:
            self.db.connect()
            QMessageBox.information(self, 'Успех', 'Соединение с базой данных установлено!')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось подключиться к базе данных:\n{e}')

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Загрузка QSS-стиля
    qss_path = os.path.join(os.path.dirname(__file__), 'styles', 'app.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    # Установка иконки приложения
    from PyQt5.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), 'styles', 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
