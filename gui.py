import sys
from configparser import ConfigParser

from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTabWidget, \
    QLineEdit, QHBoxLayout, QLabel, QCheckBox, QComboBox

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
        self.tabs.addTab(GeneratorPanel(self.npc), "PNJ 1")
        self.add_npc_button = QPushButton("Ajouter PNJ")
        self.add_npc_button.clicked.connect(lambda: self.add_npc())
        self.central_layout.addWidget(self.add_npc_button)

    def add_npc(self):
        self.nb_npc += 1
        self.tabs.addTab(GeneratorPanel(self.npc), f"PNJ {self.nb_npc}")


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

        self.generate_button = QPushButton("Générer PNJ")
        self.generate_button.clicked.connect(lambda: self.get_generated())
        self.layout.addWidget(self.generate_button)

        self.copy_npc_button = QPushButton("Copier PNJ")
        self.copy_npc_button.clicked.connect(self.get_description)
        self.layout.addWidget(self.copy_npc_button)

        game_selection = QHBoxLayout()
        game_selection.addWidget(QLabel("Jeu :"), 0, Qt.AlignRight)
        self.game_combo = QComboBox()
        self.game_combo.addItems(["Star Wars", "OGL"])
        self.game_combo.currentTextChanged.connect(self.set_characteristics)
        game_selection.addWidget(self.game_combo)
        self.layout.addLayout(game_selection)

        self.stat_button = QPushButton("Générer caractéristiques")
        self.stat_button.clicked.connect(self.get_characteristics)
        self.layout.addWidget(self.stat_button)

        self.carac_line = QHBoxLayout()

        stat_1_layout = QVBoxLayout()
        self.stat_1_label = QLabel("Vigueur")
        stat_1_layout.addWidget(self.stat_1_label, 0, Qt.AlignCenter)
        self.stat_1 = QLabel()
        stat_1_layout.addWidget(self.stat_1, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_1_layout)

        stat_2_layout = QVBoxLayout()
        self.stat_2_label = QLabel("Agilité")
        stat_2_layout.addWidget(self.stat_2_label, 0, Qt.AlignCenter)
        self.stat_2 = QLabel()
        stat_2_layout.addWidget(self.stat_2, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_2_layout)

        stat_3_layout = QVBoxLayout()
        self.stat_3_label = QLabel("Intelligence")
        stat_3_layout.addWidget(self.stat_3_label, 0, Qt.AlignCenter)
        self.stat_3 = QLabel()
        stat_3_layout.addWidget(self.stat_3, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_3_layout)

        stat_4_layout = QVBoxLayout()
        self.stat_4_label = QLabel("Ruse")
        stat_4_layout.addWidget(self.stat_4_label, 0, Qt.AlignCenter)
        self.stat_4 = QLabel()
        stat_4_layout.addWidget(self.stat_4, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_4_layout)

        stat_5_layout = QVBoxLayout()
        self.stat_5_label = QLabel("Volonté")
        stat_5_layout.addWidget(self.stat_5_label, 0, Qt.AlignCenter)
        self.stat_5 = QLabel()
        stat_5_layout.addWidget(self.stat_5, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_5_layout)

        stat_6_layout = QVBoxLayout()
        self.stat_6_label = QLabel("Présence")
        stat_6_layout.addWidget(self.stat_6_label, 0, Qt.AlignCenter)
        self.stat_6 = QLabel()
        stat_6_layout.addWidget(self.stat_6, 0, Qt.AlignCenter)
        self.carac_line.addLayout(stat_6_layout)

        self.layout.addLayout(self.carac_line)

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

    def set_characteristics(self):
        if self.game_combo.currentText() == STAR_WARS:
            self.stat_1_label.setText("Vigueur")
            self.stat_2_label.setText("Agilité")
            self.stat_3_label.setText("Intelligence")
            self.stat_4_label.setText("Ruse")
            self.stat_5_label.setText("Volonté")
            self.stat_6_label.setText("Présence")
        elif self.game_combo.currentText() == OGL:
            self.stat_1_label.setText("Force")
            self.stat_2_label.setText("Agilité")
            self.stat_3_label.setText("Constitution")
            self.stat_4_label.setText("Intelligence")
            self.stat_5_label.setText("Sagesse")
            self.stat_6_label.setText("Charisme")

    def get_characteristics(self):
        stat_1, stat_2, stat_3, stat_4, stat_5, stat_6 = \
            self.npc.get_characteristics(GAMES[self.game_combo.currentText()], self.specie_label.text().upper())
        self.stat_1.setText(str(stat_1))
        self.stat_2.setText(str(stat_2))
        self.stat_3.setText(str(stat_3))
        self.stat_4.setText(str(stat_4))
        self.stat_5.setText(str(stat_5))
        self.stat_6.setText(str(stat_6))


def main():
    app = QApplication()
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
