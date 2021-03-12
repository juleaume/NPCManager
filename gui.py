import sys
from configparser import ConfigParser

from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTabWidget, \
    QLineEdit

from manager import NPCGenerator


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("NPC Generator")
        self.setFixedWidth(1000)
        self.npc_config = ConfigParser()
        self.npc_config.read("npc.ini", "utf8")
        self.npc = NPCGenerator(self.npc_config)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.tabs = QTabWidget()
        self.central_layout.addWidget(self.tabs)
        self.nb_npc = 1
        self.tabs.addTab(GeneratorPanel(self.npc), "NPC 1")
        self.add_npc_button = QPushButton("Add NPC")
        self.add_npc_button.clicked.connect(lambda: self.add_npc())
        self.central_layout.addWidget(self.add_npc_button)

    def add_npc(self):
        self.nb_npc += 1
        self.tabs.addTab(GeneratorPanel(self.npc), f"NPC {self.nb_npc}")


class GeneratorPanel(QWidget):
    def __init__(self, npc_generator: NPCGenerator, parent=None):
        super(GeneratorPanel, self).__init__(parent)
        self.npc = npc_generator
        self.layout = QVBoxLayout()
        self.npc_label = QLineEdit()
        self.layout.addWidget(self.npc_label)
        self.generate_button = QPushButton("Generate NPC")
        self.generate_button.clicked.connect(lambda: self.get_generated(self.npc_label))
        self.layout.addWidget(self.generate_button)
        self.setLayout(self.layout)

    def get_generated(self, box: QLineEdit):
        output = self.npc.generate()
        box.setText(output)


def main():
    app = QApplication()
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
