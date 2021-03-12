import sys
from configparser import ConfigParser

from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTabWidget, \
    QLineEdit, QHBoxLayout, QLabel, QCheckBox

from manager import NPCGenerator
from constant_strings import *


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("NPC Generator")
        self.setFixedWidth(1500)
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

        self.tag_line = QHBoxLayout()
        self.tag_line.addWidget(QLabel("Tags :"))
        self.tags = QLineEdit()
        self.tag_line.addWidget(self.tags)
        self.layout.addLayout(self.tag_line)

        self.line_layout = QHBoxLayout()
        self.name_label = QLineEdit()
        self.line_layout.addWidget(self.name_label)
        self.line_layout.addWidget(QLabel("est"))
        self.job_label = QLineEdit()
        self.line_layout.addWidget(self.job_label)
        self.specie_label = QLineEdit()
        self.line_layout.addWidget(self.specie_label)
        self.line_layout.addWidget(QLabel(','))
        self.line_layout.addWidget(QLabel("d'apparence"))
        self.appearance_label = QLineEdit()
        self.line_layout.addWidget(self.appearance_label)
        self.line_layout.addWidget(QLabel(','))
        self.behavior_label = QLineEdit()
        self.line_layout.addWidget(self.behavior_label)
        self.line_layout.addWidget(QLabel(", semble être"))
        self.personality_label = QLineEdit()
        self.line_layout.addWidget(self.personality_label)
        self.layout.addLayout(self.line_layout)
        self.line_layout.addWidget(QLabel("et a"))
        self.accessories_label = QLineEdit()
        self.line_layout.addWidget(self.accessories_label)

        self.fix_line = QHBoxLayout()
        self.fix_name = QCheckBox("fixer nom")
        self.fix_line.addWidget(self.fix_name)

        self.fix_job = QCheckBox("fixer métier")
        self.fix_line.addWidget(self.fix_job)

        self.fix_specie = QCheckBox("fixer espèce")
        self.fix_line.addWidget(self.fix_specie)

        self.fix_appearance = QCheckBox("fixer apparence")
        self.fix_line.addWidget(self.fix_appearance)

        self.fix_behavior = QCheckBox("fixer comportement")
        self.fix_line.addWidget(self.fix_behavior)

        self.fix_personality = QCheckBox("fixer personnalité")
        self.fix_line.addWidget(self.fix_personality)

        self.fix_accessories = QCheckBox("fixer accessoire")
        self.fix_line.addWidget(self.fix_accessories)

        self.layout.addLayout(self.fix_line)

        self.generate_button = QPushButton("Generate NPC")
        self.generate_button.clicked.connect(lambda: self.get_generated())
        self.layout.addWidget(self.generate_button)

        self.copy_npc_button = QPushButton("Copy NPC")
        self.copy_npc_button.clicked.connect(self.get_description)
        self.layout.addWidget(self.copy_npc_button)

        self.setLayout(self.layout)

    def get_generated(self):
        traits = self.npc.generate(*self.tags.text().split(', '))
        if traits['gender'] == WOM:
            e_gender = 'e'
        elif traits['gender'] == ENB:
            e_gender = '·e'
        else:
            e_gender = ""
        if FEM in self.npc.tags[traits['accessories'].upper()]:
            det_accessories = "une"
        elif MASC in self.npc.tags[traits['accessories'].upper()]:
            det_accessories = "un"
        elif PLUR in self.npc.tags[traits['accessories'].upper()]:
            det_accessories = "de"
        elif PLURS in self.npc.tags[traits['accessories'].upper()]:
            det_accessories = "des"
        else:
            det_accessories = ""
        if not self.fix_name.isChecked():
            self.name_label.setText(traits['name'])
        if not self.fix_job.isChecked():
            self.job_label.setText(f"un{e_gender} {traits['job']}")
        if not self.fix_specie.isChecked():
            self.specie_label.setText(traits['specie'])
        if not self.fix_appearance.isChecked():
            self.appearance_label.setText(traits['appearance'])
        if not self.fix_behavior.isChecked():
            self.behavior_label.setText(traits['behavior'])
        if not self.fix_personality.isChecked():
            self.personality_label.setText(traits['personality'])
        if not self.fix_accessories.isChecked():
            self.accessories_label.setText(f"{det_accessories} {traits['accessories']}")

    def get_description(self):
        npc_description = f"{self.name_label.text()} est {self.job_label.text()} {self.specie_label.text()} " \
                          f"d'apparence {self.appearance_label.text()}, {self.behavior_label.text()}, semble être " \
                          f"{self.personality_label.text()} et a {self.accessories_label.text()}"
        QClipboard().setText(npc_description)


def main():
    app = QApplication()
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
