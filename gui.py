import sys
from configparser import ConfigParser

from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard, QFont
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTabWidget, \
    QLineEdit, QHBoxLayout, QLabel, QCheckBox, QComboBox, QTextEdit, QGroupBox

from manager import NPCGenerator
from constant_strings import *


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("NPC Generator")
        self.setFixedWidth(1750)
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
        self.tabs.addTab(GeneratorPanel(self.npc, self), "PNJ 1")
        self.add_npc_button = QPushButton("Ajouter PNJ")
        self.add_npc_button.clicked.connect(lambda: self.add_npc())
        self.central_layout.addWidget(self.add_npc_button)

    def add_npc(self):
        self.nb_npc += 1
        self.tabs.addTab(GeneratorPanel(self.npc, self), f"PNJ {self.nb_npc}")


class GeneratorPanel(QWidget):
    def __init__(self, npc_generator: NPCGenerator, parent=None):
        super(GeneratorPanel, self).__init__(parent)
        self.parent = parent
        self.npc = npc_generator
        self.layout = QVBoxLayout()

        self.tag_line = QHBoxLayout()
        self.tag_line.addWidget(QLabel("Tags :"))
        self.tags = QLineEdit()
        self.tag_line.addWidget(self.tags)
        self.layout.addLayout(self.tag_line)

        self.line_layout = QHBoxLayout()
        npc_font = QFont()
        npc_font.setPointSize(15)
        self.name_label = QLineEdit()
        self.name_label.textChanged.connect(self.set_tab_name)
        self.name_label.setFont(npc_font)
        self.line_layout.addWidget(self.name_label)
        verb_label = QLabel("est")
        verb_label.setFont(npc_font)
        self.line_layout.addWidget(verb_label)
        self.job_label = QLineEdit()
        self.job_label.setFont(npc_font)
        self.line_layout.addWidget(self.job_label)
        self.specie_label = QLineEdit()
        self.specie_label.setFont(npc_font)
        self.line_layout.addWidget(self.specie_label)
        appearance_label = QLabel("plutôt")
        appearance_label.setFont(npc_font)
        self.line_layout.addWidget(appearance_label)
        self.appearance_label = QLineEdit()
        self.appearance_label.setFont(npc_font)
        self.line_layout.addWidget(self.appearance_label)
        comma_label = QLabel(',')
        comma_label.setFont(npc_font)
        self.line_layout.addWidget(comma_label)
        self.behavior_label = QLineEdit()
        self.behavior_label.setFont(npc_font)
        self.line_layout.addWidget(self.behavior_label)
        personality_label = QLabel(", semble être")
        personality_label.setFont(npc_font)
        self.line_layout.addWidget(personality_label)
        self.personality_label = QLineEdit()
        self.personality_label.setFont(npc_font)
        self.line_layout.addWidget(self.personality_label)
        accessories_label = QLabel("et a")
        accessories_label.setFont(npc_font)
        self.line_layout.addWidget(accessories_label)
        self.accessories_label = QLineEdit()
        self.accessories_label.setFont(npc_font)
        self.line_layout.addWidget(self.accessories_label)
        self.layout.addLayout(self.line_layout)

        self.fix_line = QHBoxLayout()
        self.fixes = list()
        self.fix_name = QCheckBox("fixer nom")
        self.fixes.append(self.fix_name)
        self.fix_line.addWidget(self.fix_name)

        self.fix_job = QCheckBox("fixer métier")
        self.fixes.append(self.fix_job)
        self.fix_line.addWidget(self.fix_job)

        self.fix_specie = QCheckBox("fixer espèce")
        self.fixes.append(self.fix_specie)
        self.fix_line.addWidget(self.fix_specie)

        self.fix_appearance = QCheckBox("fixer apparence")
        self.fixes.append(self.fix_appearance)
        self.fix_line.addWidget(self.fix_appearance)

        self.fix_behavior = QCheckBox("fixer comportement")
        self.fixes.append(self.fix_behavior)
        self.fix_line.addWidget(self.fix_behavior)

        self.fix_personality = QCheckBox("fixer personnalité")
        self.fixes.append(self.fix_personality)
        self.fix_line.addWidget(self.fix_personality)

        self.fix_accessories = QCheckBox("fixer accessoire")
        self.fixes.append(self.fix_accessories)
        self.fix_line.addWidget(self.fix_accessories)

        self.layout.addLayout(self.fix_line)

        fix_buttons_lines = QHBoxLayout()
        self.reset_button = QPushButton("Libérer tous les champs")
        self.reset_button.clicked.connect(self.reset_all_fixes)
        fix_buttons_lines.addWidget(self.reset_button)
        self.fix_all_button = QPushButton("Fixer tous les champs")
        self.fix_all_button.clicked.connect(self.set_all_fixes)
        fix_buttons_lines.addWidget(self.fix_all_button)
        self.invert_button = QPushButton("Inverser les champs")
        self.invert_button.clicked.connect(self.invert_all_fixes)
        fix_buttons_lines.addWidget(self.invert_button)

        self.layout.addLayout(fix_buttons_lines)

        self.generate_button = QPushButton("Générer PNJ")
        self.generate_button.setFixedHeight(75)
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
        self.stat_button.setFixedHeight(75)
        self.stat_button.clicked.connect(self.get_characteristics)
        self.layout.addWidget(self.stat_button)

        self.carac_line = QHBoxLayout()

        stat_font = QFont()
        stat_font.setPointSize(50)
        self.stat_1_group = QGroupBox("Vigueur")
        stat_1_layout = QVBoxLayout()
        self.stat_1 = QLabel()
        self.stat_1.setFont(stat_font)
        stat_1_layout.addWidget(self.stat_1, 0, Qt.AlignCenter)
        self.stat_1_group.setLayout(stat_1_layout)
        self.carac_line.addWidget(self.stat_1_group)

        self.stat_2_group = QGroupBox("Agilité")
        stat_2_layout = QVBoxLayout()
        self.stat_2 = QLabel()
        self.stat_2.setFont(stat_font)
        stat_2_layout.addWidget(self.stat_2, 0, Qt.AlignCenter)
        self.stat_2_group.setLayout(stat_2_layout)
        self.carac_line.addWidget(self.stat_2_group)

        self.stat_3_group = QGroupBox("Intelligence")
        stat_3_layout = QVBoxLayout()
        self.stat_3 = QLabel()
        self.stat_3.setFont(stat_font)
        stat_3_layout.addWidget(self.stat_3, 0, Qt.AlignCenter)
        self.stat_3_group.setLayout(stat_3_layout)
        self.carac_line.addWidget(self.stat_3_group)

        self.stat_4_group = QGroupBox("Ruse")
        stat_4_layout = QVBoxLayout()
        self.stat_4 = QLabel()
        self.stat_4.setFont(stat_font)
        stat_4_layout.addWidget(self.stat_4, 0, Qt.AlignCenter)
        self.stat_4_group.setLayout(stat_4_layout)
        self.carac_line.addWidget(self.stat_4_group)

        self.stat_5_group = QGroupBox("Volonté")
        stat_5_layout = QVBoxLayout()
        self.stat_5 = QLabel()
        self.stat_5.setFont(stat_font)
        stat_5_layout.addWidget(self.stat_5, 0, Qt.AlignCenter)
        self.stat_5_group.setLayout(stat_5_layout)
        self.carac_line.addWidget(self.stat_5_group)

        self.stat_6_group = QGroupBox("Présence")
        stat_6_layout = QVBoxLayout()
        self.stat_6 = QLabel()
        self.stat_6.setFont(stat_font)
        stat_6_layout.addWidget(self.stat_6, 0, Qt.AlignCenter)
        self.stat_6_group.setLayout(stat_6_layout)
        self.carac_line.addWidget(self.stat_6_group)

        self.layout.addLayout(self.carac_line)

        note_group = QGroupBox("Notes")
        note_layout = QVBoxLayout()
        self.additional_note = QTextEdit()
        note_layout.addWidget(self.additional_note)
        note_group.setLayout(note_layout)
        self.layout.addWidget(note_group)

        self.setLayout(self.layout)

    def set_all_fixes(self):
        for box in self.fixes:
            box.setChecked(True)

    def reset_all_fixes(self):
        for box in self.fixes:
            box.setChecked(False)

    def invert_all_fixes(self):
        for box in self.fixes:
            box.setChecked(not box.isChecked())

    def get_generated(self):
        traits = self.npc.generate(*self.tags.text().split(', '))
        if traits['gender'] == WOM:
            e_gender = 'e'
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

    def set_tab_name(self):
        self.parent.tabs.setTabText(self.parent.tabs.currentIndex(), self.name_label.text())

    def get_description(self):
        npc_description = f"{self.name_label.text()} est {self.job_label.text()} {self.specie_label.text()} " \
                          f"plutôt {self.appearance_label.text()}, {self.behavior_label.text()}, semble être " \
                          f"{self.personality_label.text()} et a {self.accessories_label.text()}"
        QClipboard().setText(npc_description)

    def set_characteristics(self):
        if self.game_combo.currentText() == STAR_WARS:
            self.stat_1_group.setTitle("Vigueur")
            self.stat_2_group.setTitle("Agilité")
            self.stat_3_group.setTitle("Intelligence")
            self.stat_4_group.setTitle("Ruse")
            self.stat_5_group.setTitle("Volonté")
            self.stat_6_group.setTitle("Présence")
        elif self.game_combo.currentText() == OGL:
            self.stat_1_group.setTitle("Force")
            self.stat_2_group.setTitle("Dexterité")
            self.stat_3_group.setTitle("Constitution")
            self.stat_4_group.setTitle("Intelligence")
            self.stat_5_group.setTitle("Sagesse")
            self.stat_6_group.setTitle("Charisme")

    def get_characteristics(self):
        stat_1, stat_2, stat_3, stat_4, stat_5, stat_6 = \
            self.npc.get_characteristics(GAMES[self.game_combo.currentText()], self.specie_label.text().upper())
        self.stat_1.setText(f"{stat_1}")
        self.stat_2.setText(f"{stat_2}")
        self.stat_3.setText(f"{stat_3}")
        self.stat_4.setText(f"{stat_4}")
        self.stat_5.setText(f"{stat_5}")
        self.stat_6.setText(f"{stat_6}")


def main():
    app = QApplication()
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
