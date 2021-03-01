from configparser import ConfigParser
import random

GENDERED = "gendered"
MASC = "masc"
FEM = "fem"
UNI = "uni"
WOM = 'w'
MAN = 'm'
ENB = 'n'
GENDERS = {WOM, MAN, ENB}


class NPCGenerator:

    def __init__(self, config):
        self.config = config
        self.traits, self.tags = self.get_config()

    def get_config(self):
        traits = dict()
        tags = dict()
        for sec in self.config:
            traits[sec] = list()
            for el in self.config[sec]:
                tags[el.upper()] = set()
                traits[sec].append(el)
                for tag in self.config[sec][el].split(','):
                    tags[el.upper()].add(tag.strip())
        return traits, tags

    def generate(self, *tags):
        name = self.select_trait("NAMES", tags)
        if not bool(set(tags).intersection(GENDERS)):
            gender = self.get_gender(name)
        else:
            gender = random.choice(list(set(tags).intersection(GENDERS)))
        specie = self.get_gendered_trait(gender, "SPECIES", tags)
        if gender == WOM:
            e_gender = 'e'
        elif gender == ENB:
            e_gender = '·e'
        else:
            e_gender = ""
        job = self.get_gendered_trait(gender, "JOBS", tags)
        appearance = self.select_trait("APPEARANCES", tags).lower()
        behavior = self.select_trait("BEHAVIOR", tags).lower()
        e_behavior = "e" if FEM in self.tags[behavior.upper()] else ""
        personality = self.get_gendered_trait(gender, "PERSONALITY", tags).lower()
        personality_e = ""
        if GENDERED in self.tags[personality.upper()]:
            if gender == WOM:
                personality_e = "e"
            elif gender == ENB:
                personality_e = "·e"

        accessories = self.select_trait("ACCESSORIES", tags).lower()
        e_accessories = "e" if FEM in self.tags[accessories.upper()] else ""

        print(
            f"{name} est un{e_gender} {job} {specie} d'apparence {appearance}, a un{e_behavior} {behavior}, "
            f"semble être {personality}{personality_e} et porte un{e_accessories} {accessories}")

    def get_gender(self, name: str):
        tags = self.tags[name.upper()]
        if GENDERS.issubset(tags):
            return random.choice(list(GENDERS))
        elif {WOM, ENB}.issubset(tags):
            return random.choice([WOM, ENB])
        elif {MAN, ENB}.issubset(tags):
            return random.choice([MAN, ENB])
        elif {WOM, MAN}.issubset(tags):
            return random.choice([WOM, MAN])
        elif WOM in tags:
            return WOM
        elif MASC in tags:
            return MASC
        elif ENB in tags:
            return ENB
        else:
            return random.choice(list(GENDERS))

    def get_gendered_trait(self, gender: str, trait, tags):
        while True:
            selected_trait = self.select_trait(trait, tags)
            genders = GENDERS.intersection(self.tags[selected_trait.upper()])
            if not genders or gender in genders:
                if gender == WOM and GENDERED in self.tags[selected_trait.upper()]:
                    return f"{selected_trait}e"
                else:
                    return selected_trait
            else:
                if GENDERED in self.tags[selected_trait.upper()]:
                    if gender == WOM:
                        return f"{selected_trait}e"
                    elif gender == ENB:
                        return f"{selected_trait}·e"
                    elif gender == MAN:
                        return selected_trait

    def get_trait(self, trait):
        return random.choice(self.traits[trait]).capitalize()

    def get_tags(self, section):
        tags = list()
        for traits in self.config[section]:
            trait_set = set()
            for t in self.config[section][traits].split(','):
                trait_set.add(t.strip())
            tags.append(trait_set)
        return tags

    def select_trait(self, trait: str, tags) -> str:
        tags = set(tags)
        selected_trait = self.get_trait(trait)
        if not self.check_tag(trait, tags):
            return selected_trait
        while not tags.issubset(set(self.tags[selected_trait.upper()])):
            selected_trait = self.get_trait(trait)
        return selected_trait

    def check_tag(self, section, tags):
        tags_list = self.get_tags(section)
        for tag in tags_list:
            if set(tags).issubset(tag):
                return True
        return False


if __name__ == '__main__':
    npc = ConfigParser()
    npc.read("npc.ini", "utf8")
    npc_generator = NPCGenerator(npc)
    npc_generator.generate('n')
