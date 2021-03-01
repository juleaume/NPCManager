from configparser import ConfigParser
import random

MASC = "masc"
FEM = "fem"
UNI = "uni"

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
        appearance = self.select_trait("APPEARANCES", tags).lower()
        behavior = self.select_trait("BEHAVIOR", tags).lower()
        e_behavior = "e" if FEM in self.tags[behavior.upper()] else ""
        personality = self.select_trait("PERSONALITY", tags).lower()
        e_personality = "e" if FEM in self.tags[personality.upper()] else ""
        accessories = self.select_trait("ACCESSORIES", tags).lower()
        e_accessories = "e" if FEM in self.tags[accessories.upper()] else ""

        print(
            f"{name} est d'apparence {appearance}, a un{e_behavior} {behavior}, semble être {personality} et porte un{e_accessories} {accessories}")

    def get_trait(self, trait):
        return random.choice(self.traits[trait]).capitalize()

    def get_tags(self, section):
        tags = set()
        for traits in self.config[section]:
            for t in self.config[section][traits].split(','):
                if t.strip() not in tags:
                    tags.add(t.strip())
        return tags

    def select_trait(self, trait: str, tags):
        tags = set(tags)
        tags = tags.intersection(self.get_tags(trait))
        selected_trait = self.get_trait(trait)
        if not self.check_tag(trait, tags):
            return selected_trait
        while not tags.issubset(set(self.tags[selected_trait.upper()])):
            selected_trait = self.get_trait(trait)
        return selected_trait

    def check_tag(self, section, tags):
        tags_list = self.get_tags(section)
        return set(tags).issubset(tags_list)


if __name__ == '__main__':
    npc = ConfigParser()
    npc.read("npc.ini", "utf8")
    npc_generator = NPCGenerator(npc)
    npc_generator.generate("prenom", "fantasy")
