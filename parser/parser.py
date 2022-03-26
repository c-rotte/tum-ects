import copy
import random
import string

import requests
from bs4 import BeautifulSoup

from database import Database


def add_element_to_dict(dic: dict, elem, parent_keys: [str], new_key: str):
    """adds element to nested dict. Creates empty dicts for non-existent parent_keys"""
    current_dic = dic
    for key in parent_keys:
        try:
            current_dic = current_dic[key]
        except KeyError:
            current_dic[key] = {}
            current_dic = current_dic[key]

    current_dic[new_key] = elem


class Parser:

    def __init__(self, database: Database):
        self.database = database

    def _switch_to_english(self, PSESSIONID):
        """switches the web session to english"""
        requests.post("https://campus.tum.de/tumonline/pl/ui/$ctx/wbOAuth2.language",
                      headers={"cookie": f"PSESSIONID={PSESSIONID}"},
                      data={"language": "EN"})

    def _parse_node(self, pStpStpNr, node_id, GERMAN_PSESSIONID, ENGLISH_PSESSIONID, parent_keys_de, parent_keys_en,
                    curriculum_de, curriculum_en):
        """parses a single node in the curriculum tree. For courses: appends it to the list of
        courses, adds course info to curriculum dict. Everything else: adds node in curriculum dict and descents"""

        r_german = requests.get(f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbStpCs.cbSpoTree?"
                                f"pStStudiumNr=&pStpStpNr={pStpStpNr}&pStPersonNr=&pSJNr=&pIsStudSicht=FALSE&pShowErg=J&"
                                f"pHideInactive=TRUE&pCaller=&pStpKnotenNr={node_id}&pId=&pAction=0",
                                headers={"cookie": f"PSESSIONID={GERMAN_PSESSIONID}"})
        r_english = requests.get(f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbStpCs.cbSpoTree?"
                                 f"pStStudiumNr=&pStpStpNr={pStpStpNr}&pStPersonNr=&pSJNr=&pIsStudSicht=FALSE&pShowErg=J&"
                                 f"pHideInactive=TRUE&pCaller=&pStpKnotenNr={node_id}&pId=&pAction=0",
                                 headers={"cookie": f"PSESSIONID={ENGLISH_PSESSIONID}"})

        soup_german = BeautifulSoup(r_german.text, "lxml")
        soup_english = BeautifulSoup(r_english.text, "lxml")

        german_nodes = soup_german.find_all("a", {"class": "KnotenLink"})
        english_nodes = soup_english.find_all("a", {"class": "KnotenLink"})

        assert (len(german_nodes) == len(english_nodes))

        for node_german, node_english in zip(german_nodes, english_nodes):

            node_type = node_german.span.get("title")

            # parse module and add element to curriculum dict
            if "Modul" in node_type:
                parent_node = node_german.find_parent("tr")
                module_id = "none"
                # extract module information
                if "[" in node_german.span.text and "]" in node_german.span.text:
                    module_id = node_german.span.text.split("[")[1].split("]")[0]
                node_tds = parent_node.find_all("td", {"class": "R"})
                node_ects = node_tds[0].div.span.text.replace(",", ".").strip()
                node_weighting_factor = node_tds[1].div.span.text.replace(",", ".").strip()
                german_title = node_german.span.text.strip()
                english_title = node_english.span.text.strip()

                # create info dicts
                module_info_de = {
                    "module_id": module_id,
                    "ects": 0 if node_ects == "" else float(node_ects),
                    "weighting_factor": 0 if node_weighting_factor == "" else float(node_weighting_factor),
                    "title": german_title
                }
                module_info_en = copy.copy(module_info_de)
                module_info_en["title"] = english_title

                add_element_to_dict(curriculum_de, module_info_de, parent_keys_de, module_id)
                add_element_to_dict(curriculum_en, module_info_en, parent_keys_en, module_id)
                continue

            # parse rule node and add to dict, recursively continue with rule node
            add_element_to_dict(curriculum_de, {}, parent_keys_de, node_german.span.text.strip())
            add_element_to_dict(curriculum_en, {}, parent_keys_en, node_english.span.text.strip())
            new_node_id = node_german.get("id").replace("kn", "").replace("-toggle", "")
            self._parse_node(pStpStpNr,
                             new_node_id,
                             GERMAN_PSESSIONID,
                             ENGLISH_PSESSIONID,
                             parent_keys_de + [node_german.span.text.strip()],
                             parent_keys_en + [node_english.span.text.strip()],
                             curriculum_de,
                             curriculum_en)

    def _get_for_pStpStpNr(self, pStpStpNr):
        """returns a list of all courses in the given degree and a dict containing the curriculum of the degree"""
        GERMAN_PSESSIONID = "".join(random.choices(string.ascii_uppercase + string.digits, k=64))
        ENGLISH_PSESSIONID = "".join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self._switch_to_english(ENGLISH_PSESSIONID)

        r_german = requests.get(
            f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
            f"pStpStpNr={pStpStpNr}",
            headers={"cookie": f"PSESSIONID={GERMAN_PSESSIONID}"})
        soup_german = BeautifulSoup(r_german.text, "html.parser")

        if "Curriculum Support" in soup_german.head.title.text:
            return None, None

        r_english = requests.get(
            f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
            f"pStpStpNr={pStpStpNr}",
            headers={"cookie": f"PSESSIONID={ENGLISH_PSESSIONID}"})
        soup_english = BeautifulSoup(r_english.text, "html.parser")

        # extracting titles from response
        title_german = soup_german.find("span", {"title": "SPO-Version "}).text
        title_english = soup_english.find("span", {"title": "Curriculum version "}).text
        subtitle_german = soup_german.find("td", {"class": "pageOwner"}).span.text
        subtitle_english = soup_english.find("td", {"class": "pageOwner"}).span.text

        curriculum_id = \
            title_german.split("[")[1].split("]")[0] if "[" in title_german and "]" in title_german else "unknown"

        print(f"({pStpStpNr}) Parsing {title_german}...")

        main_node = soup_german.find("a", {"class": "KnotenLink"})

        degree_info_de = {"degree_id": subtitle_german[0:6],
                          "title": title_german,
                          "subtitle": subtitle_german,
                          "curriculum_id": curriculum_id}
        degree_info_en = {"degree_id": subtitle_german[0:6],
                          "title": title_english,
                          "subtitle": subtitle_english,
                          "curriculum_id": curriculum_id}

        curriculum_de = {title_german: {}}
        curriculum_en = {title_english: {}}

        if main_node:
            main_node_id = main_node.get("id").replace("kn", "").replace("-toggle", "")
            self._parse_node(pStpStpNr,  # Number of degree
                             main_node_id,  # start point of recursive descent into curriculum
                             GERMAN_PSESSIONID,  # session ID for german requests
                             ENGLISH_PSESSIONID,  # session ID for english requests
                             [title_german],  # acc for the keys in recursive descent, used for german curriculum
                             [title_english],  # acc for the keys in recursive descent, used for english curriculum
                             curriculum_de,  # dict used to store the german curriculum
                             curriculum_en)  # dict used to store the english curriculum
        degree_info_de["curriculum"] = curriculum_de
        degree_info_en["curriculum"] = curriculum_en
        return degree_info_de, degree_info_en

    def _process_pStpStpNr(self, pStpStpNr):
        print(f"Checking pStpStpNr {pStpStpNr}...")
        degree_info_de, degree_info_en = self._get_for_pStpStpNr(pStpStpNr)
        # remove old data
        self.database.remove_degree(pStpStpNr)
        self.database.remove_curriculum(pStpStpNr, language="german")
        self.database.remove_curriculum(pStpStpNr, language="english")
        if not degree_info_de or not degree_info_en:
            return
        # add new data
        degree_info_de["pStpStpNr"] = pStpStpNr
        degree_info_en["pStpStpNr"] = pStpStpNr
        self.database.add_curriculum(degree_info_de, language="german")
        self.database.add_curriculum(degree_info_en, language="english")

    def run(self):
        # check all numbers
        for pStpStpNr in range(0, 10000):
            try:
                self._process_pStpStpNr(pStpStpNr)
            except Exception as e:
                return e
        return None
