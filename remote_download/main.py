import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog, 
                             QLabel, QProgressBar, QMessageBox, QDialog, QLineEdit,
                             QCheckBox, QHeaderView)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
import requests

SERVER_URL = "http://100.124.166.5:5000"
TIMEOUT = 3000

session = requests.Session()

def login(password):
    try:
        response = session.post(f"{SERVER_URL}/login", json={"password": password}, timeout=TIMEOUT)
        if response.status_code == 200:
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return False


def logout():
    try:
        response = session.get(f"{SERVER_URL}/logout", timeout=TIMEOUT)
        if response.status_code == 200:
            print("Logged out successfully")
        else:
            print("Logout failed")
    except requests.exceptions.RequestException as e:
        print(f"Error during logout: {e}")

def get_directory_structure():
    try:
        response = session.get(f"{SERVER_URL}/list_files", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Authentication required. Please log in.")
            return None
        else:
            print(f"Failed to get directory structure. Status code: {response.status_code}")
            print("Response content:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        return None

class DownloadThread(QThread):
    progress_update = pyqtSignal(str, int)
    download_complete = pyqtSignal(str, bool)

    def __init__(self, file_path, save_path):
        super().__init__()
        self.file_path = file_path
        self.save_path = save_path

    def run(self):
        try:
            url = f"{SERVER_URL}/download"
            params = {'path': self.file_path}
            response = session.get(url, params=params, stream=True)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024  # 1 KB
                written = 0
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        written += len(data)
                        file.write(data)
                        if total_size > 0:
                            percent = int((written / total_size) * 100)
                            self.progress_update.emit(self.file_path, percent)
                self.download_complete.emit(self.file_path, True)
            else:
                self.download_complete.emit(self.file_path, False)
        except Exception as e:
            print(f"Download error: {e}")
            self.download_complete.emit(self.file_path, False)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setFixedSize(300, 100)
        layout = QVBoxLayout(self)
        
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter password')
        layout.addWidget(self.password_input)
        
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.try_login)
        layout.addWidget(self.login_button)

    def try_login(self):
        if login(self.password_input.text()):
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid password. Please try again.')

class DownloadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_threads = {}

    def initUI(self):
        self.setWindowTitle('Advanced File Browser and Downloader')
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search files...')
        self.search_bar.textChanged.connect(self.filter_files)
        main_layout.addWidget(self.search_bar)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 100)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        main_layout.addWidget(self.tree)
        
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.setIcon(QIcon('refresh_icon.png'))
        self.download_button = QPushButton('Download Selected')
        self.download_button.setIcon(QIcon('download_icon.png'))
        self.logout_button = QPushButton('Logout')
        self.logout_button.setIcon(QIcon('logout_icon.png'))
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(button_layout)
        
        self.status_label = QLabel('Ready')
        main_layout.addWidget(self.status_label)
        
        self.refresh_button.clicked.connect(self.refresh_directory)
        self.download_button.clicked.connect(self.download_selected_files)
        self.logout_button.clicked.connect(self.logout)
        
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #f0f0f0;
            }
            QTreeWidget {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
            QTreeWidget::item {
                height: 25px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLabel {
                font-size: 14px;
            }
            QProgressBar {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        self.show_login_dialog()

    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_directory()
        else:
            self.close()

    def refresh_directory(self):
        self.tree.clear()
        self.status_label.setText('Refreshing directory...')
        directory_structure = get_directory_structure()
        if directory_structure is not None:
            self.populate_tree(self.tree.invisibleRootItem(), directory_structure)
            self.status_label.setText('Directory refreshed')
        else:
            self.status_label.setText('Failed to refresh directory')
            self.show_login_dialog()

    def populate_tree(self, parent, structure):
        for name, value in structure.items():
            if value == "file":
                item = QTreeWidgetItem(parent, [name, "File", "Unknown"])
                item.setIcon(0, QIcon('file_icon.png'))
            else:
                folder = QTreeWidgetItem(parent, [name, "Folder", ""])
                folder.setIcon(0, QIcon('folder_icon.png'))
                self.populate_tree(folder, value)

    def filter_files(self, text):
        for i in range(self.tree.topLevelItemCount()):
            self.filter_tree_item(self.tree.topLevelItem(i), text.lower())

    def filter_tree_item(self, item, text):
        is_visible = text in item.text(0).lower()
        if item.childCount() > 0:
            for i in range(item.childCount()):
                child_visible = self.filter_tree_item(item.child(i), text)
                is_visible = is_visible or child_visible
        item.setHidden(not is_visible)
        return is_visible

    def download_selected_files(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            for item in selected_items:
                if item.text(1) == "File":
                    file_path = self.get_file_path(item)
                    save_path, _ = QFileDialog.getSaveFileName(self, "Save File", item.text(0))
                    if save_path:
                        self.start_download(file_path, save_path)
        else:
            QMessageBox.warning(self, "No Selection", "Please select files to download.")

    def start_download(self, file_path, save_path):
        thread = DownloadThread(file_path, save_path)
        thread.progress_update.connect(self.update_progress)
        thread.download_complete.connect(self.download_finished)
        thread.start()
        self.download_threads[file_path] = thread
        self.status_label.setText(f'Downloading {os.path.basename(file_path)}...')

    def update_progress(self, file_path, percent):
        self.status_label.setText(f'Downloading {os.path.basename(file_path)}: {percent}%')

    def download_finished(self, file_path, success):
        if success:
            self.status_label.setText(f'{os.path.basename(file_path)} downloaded successfully')
        else:
            self.status_label.setText(f'Failed to download {os.path.basename(file_path)}')
        del self.download_threads[file_path]

    def get_file_path(self, item):
        path = []
        while item is not None:
            path.append(item.text(0))
            item = item.parent()
        return "/".join(reversed(path))

    def logout(self):
        logout()
        self.tree.clear()
        self.status_label.setText('Logged out')
        self.show_login_dialog()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DownloadApp()
    ex.show()
    sys.exit(app.exec_())