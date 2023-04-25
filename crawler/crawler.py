import json
import random
import string
import unicodedata

import bs4
import requests
from bs4 import BeautifulSoup

from requests import RequestException
from retry import retry


class Crawler:

    def __init__(self):
        self.url_base = "https://campus.tum.de/tumonline/pl/ui/$ctx"
        self.german_p_session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self.english_p_session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self._switch_to_english(self.english_p_session_id)

    def _get_p_session_id(self, english: bool):
        if english:
            return self.english_p_session_id
        else:
            return self.german_p_session_id

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def _switch_to_english(self, p_session_id):
        """switches the web session to english"""
        requests.post(f'{self.url_base}/wbOAuth2.language',
                      headers={'cookie': f'PSESSIONID={p_session_id}'},
                      data={'language': 'EN'})

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def degrees(self, english: bool):
        """returns a list of all degrees"""
        p_session_id = self._get_p_session_id(english)
        res = requests.get(
            "https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbShow?pOrgNr=1&pId=tabIdSPOModules_tabid&pTabContainerId=",
            headers={'cookie': f'PSESSIONID={p_session_id}'})
        soup = BeautifulSoup(res.text, "html.crawler")
        all_cdata = soup.find_all(text=lambda tag: isinstance(tag, bs4.CData))
        cdata = max([x.string for x in all_cdata], key=len)
        degrees_json = cdata.split("=")[1].strip().rstrip(";")
        # remove '\' from json
        degrees_json = degrees_json.replace("\\", "")
        # remove all control characters
        degrees_json = "".join(c for c in degrees_json if unicodedata.category(c)[0] != "C")
        degrees_json = json.loads(degrees_json, strict=False)
        return degrees_json["data"]

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def modules(self, english: bool):
        """returns a list of all modules"""
        p_session_id = self._get_p_session_id(english)
        res = requests.get(
            f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules',
            headers={'cookie': f'PSESSIONID={p_session_id}'})
        soup = BeautifulSoup(res.text, "lxml")
        # first, check if we have any modules
        if soup.find("tr", {"class": "cNoEntry"}):
            return
        # if we have modules, get the number of pages
        page_select = soup.find("select", {"name": "pPageNr"})
        number_of_pages = len(page_select.find_all("option"))
        for page_index in range(number_of_pages):
            # get the modules on the current page
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules&pPageNr={page_index + 1}',
                headers={'cookie': f'PSESSIONID={p_session_id}'})
            soup = BeautifulSoup(res.text, "lxml")
            table = soup.find("table", {"id": "idModHBTableORG"})
            for td in table.find("tbody").find_all("td"):
                # get the module id and name
                a_list = td.find_all("a")
                if len(a_list) < 2:
                    continue
                href = a_list[1].get("href")
                if "pKnotenNr" not in href:
                    continue
                name = a_list[1].next.string.strip()
                module_id = href.split("pKnotenNr=")[1].split("&")[0]
                yield module_id, name

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def module_degree_mappings(self, module_id: str, english: bool):
        """returns a list of all degree programs containing the module"""
        p_session_id = self._get_p_session_id(english)
        language_str = "EN" if english else "DE"

        def craft_url(page_nr=1):
            url = ("https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbUpdateCurrAssignmentTable?"
                   f"pOrgNr=1&pExtView=J&pKnotenNr={module_id}&pTableId=curr_assignment_table_{language_str}_{module_id}&"
                   f"pLangCode={language_str}&pExtFetching=J&pPageNr={page_nr}&pSort=&pFilter=")
            return url

        res = requests.get(craft_url(), headers={'cookie': f'PSESSIONID={p_session_id}'})
        soup = BeautifulSoup(res.text, "lxml")
        select = soup.find("td", {"class": "coTableNaviPageSelect"})
        # if we have more than one page, get the number of pages
        pages = int(select.find("select").next_sibling.text.strip()
                    .replace("of ", "").replace("von ", "")) if select else 1
        for page in range(pages):
            res = requests.get(craft_url(page + 1), headers={'cookie': f'PSESSIONID={p_session_id}'})
            soup = BeautifulSoup(res.text, "lxml")
            tbody = soup.find("table", {"class": "cotable"}).find("tbody")
            for tr in tbody.find_all("tr"):
                # get the degree program id and name
                td_list = tr.find_all("td")
                if len(td_list) < 13:
                    continue

                def text_from_td(td):
                    elements = td.find_all(text=True)
                    if not elements:
                        return None
                    return elements[0].text.strip()

                names = list(map(text_from_td, td_list))
                if len(names) < 13:
                    continue
                pStpStpNr = td_list[2].find("a").get("href").split("pStpStpNr=")[1].split("&")[0]
                yield {
                    "full_name": names[1],
                    "curriculum_version": names[2],
                    "ects": float(names[5].replace(",", ".")) if names[5] else None,
                    "weighting_factor": float(names[8].replace(",", ".")) if names[8] else None,
                    "valid_from": names[11],
                    "valid_to": names[12],
                    "pStpStpNr": pStpStpNr
                }
