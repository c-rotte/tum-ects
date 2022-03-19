import random
import string

import requests
from bs4 import BeautifulSoup

from database import Database


class Parser:

    def __init__(self, database: Database):
        self.database = database
        requests.adapters.DEFAULT_RETRIES = 5

    def switch_to_english(self, PSESSIONID):
        requests.post("https://campus.tum.de/tumonline/pl/ui/$ctx/wbOAuth2.language",
                      headers={"cookie": f"PSESSIONID={PSESSIONID}"},
                      data={"language": "EN"})

    def parse_node(self, pStpStpNr, node_id, GERMAN_PSESSIONID, ENGLISH_PSESSIONID, acc_list):
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

            if "Modul" in node_type:
                parent_node = node_german.find_parent("tr")
                module_id = "none"
                if "[" in node_german.span.text and "]" in node_german.span.text:
                    module_id = node_german.span.text.split("[")[1].split("]")[0]
                node_tds = parent_node.find_all("td", {"class": "R"})
                node_ects = node_tds[0].div.span.text.replace(",", ".").strip()
                node_weighting_factor = node_tds[1].div.span.text.replace(",", ".").strip()
                acc_list.append({
                    "module_id": module_id,
                    "title": {
                        "german": node_german.span.text.strip(),
                        "english": node_english.span.text.strip()
                    },
                    "ects": 0 if node_ects == "" else float(node_ects),
                    "weighting_factor": 0 if node_weighting_factor == "" else float(node_weighting_factor)
                })
                continue

            node_id = node_german.get("id").replace("kn", "").replace("-toggle", "")
            self.parse_node(pStpStpNr, node_id, GERMAN_PSESSIONID, ENGLISH_PSESSIONID, acc_list)

        return acc_list

    def add_pStpStpNr(self, pStpStpNr):
        GERMAN_PSESSIONID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        ENGLISH_PSESSIONID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self.switch_to_english(ENGLISH_PSESSIONID)

        r_german = requests.get(
            f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
            f"pStpStpNr={pStpStpNr}",
            headers={"cookie": f"PSESSIONID={GERMAN_PSESSIONID}"})
        soup_german = BeautifulSoup(r_german.text, "html.parser")

        if "Curriculum Support" in soup_german.head.title.text:
            return None

        r_english = requests.get(
            f"https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
            f"pStpStpNr={pStpStpNr}",
            headers={"cookie": f"PSESSIONID={ENGLISH_PSESSIONID}"})
        soup_english = BeautifulSoup(r_english.text, "html.parser")

        title_german = soup_german.find("span", {"title": "SPO-Version "}).text
        title_english = soup_english.find("span", {"title": "Curriculum version "}).text
        subtitle_german = soup_german.find("td", {"class": "pageOwner"}).span.text
        subtitle_english = soup_english.find("td", {"class": "pageOwner"}).span.text

        print(f"({pStpStpNr}) Parsing {title_german}...")

        main_node = soup_german.find("a", {"class": "KnotenLink"})

        courses = []
        if main_node:
            main_node_id = main_node.get("id").replace("kn", "").replace("-toggle", "")
            courses = self.parse_node(pStpStpNr, main_node_id, GERMAN_PSESSIONID, ENGLISH_PSESSIONID, [])

        return {
            "degree_id": subtitle_german[0:6],
            "title": {
                "german": title_german,
                "english": title_english
            },
            "subtitle": {
                "german": subtitle_german,
                "english": subtitle_english
            },
            "courses": courses
        }

    def run(self):
        for pStpStpNr in range(0, 10000):
            print(f"Checking pStpStpNr {pStpStpNr}...")
            try:
                result = self.add_pStpStpNr(pStpStpNr)
                self.database.remove_degree(pStpStpNr)
                if result:
                    print(f'Parsed {len(result["courses"])} entries')
                    self.database.add_degree(pStpStpNr, result)
            except Exception as e:
                return e
        return None








