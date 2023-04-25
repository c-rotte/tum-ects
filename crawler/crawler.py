import random
import string
import requests
from requests import RequestException
from retry import retry
import parser
from collections.abc import Iterator


class Crawler:

    def __init__(self):
        self.url_base = "https://campus.tum.de/tumonline/pl/ui/$ctx"
        self.german_p_session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self.english_p_session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
        self._switch_to_english(self.english_p_session_id)

    def _get_p_session_id(self, english: bool) -> str:
        if english:
            return self.english_p_session_id
        else:
            return self.german_p_session_id

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def _switch_to_english(self, p_session_id) -> None:
        """switches the web session to english"""
        requests.post(f'{self.url_base}/wbOAuth2.language',
                      headers={'cookie': f'PSESSIONID={p_session_id}'},
                      data={'language': 'EN'})

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def degrees(self, english: bool) -> list:
        """returns a list of all degrees"""
        p_session_id = self._get_p_session_id(english)
        res = requests.get(
            "https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbShow?"
            "pOrgNr=1&pId=tabIdSPOModules_tabid&pTabContainerId=",
            headers={'cookie': f'PSESSIONID={p_session_id}'})
        return parser.parse_degrees(res.text)

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def modules(self, english: bool) -> Iterator[str, str]:
        """returns a list of all modules"""
        p_session_id = self._get_p_session_id(english)
        res = requests.get(
            f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules',
            headers={'cookie': f'PSESSIONID={p_session_id}'})
        number_of_pages = parser.module_page_number(res.text)
        for page_index in range(number_of_pages):
            # get the modules on the current page
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules&pPageNr={page_index + 1}',
                headers={'cookie': f'PSESSIONID={p_session_id}'})
            for module_id, name in parser.parse_modules_on_page(res.text):
                yield module_id, name

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def module_degree_mappings(self, module_id: str, english: bool) -> Iterator[dict]:
        """returns a list of all degree programs containing the module"""
        p_session_id = self._get_p_session_id(english)
        language_str = "EN" if english else "DE"

        def craft_url(page_nr=1):
            url = ("https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbUpdateCurrAssignmentTable?"
                   f"pOrgNr=1&pExtView=J&pKnotenNr={module_id}"
                   f"&pTableId=curr_assignment_table_{language_str}_{module_id}&"
                   f"pLangCode={language_str}&pExtFetching=J&pPageNr={page_nr}&pSort=&pFilter=")
            return url

        res = requests.get(craft_url(), headers={'cookie': f'PSESSIONID={p_session_id}'})
        pages = parser.mapping_page_number(res.text)
        for page in range(pages):
            res = requests.get(craft_url(page + 1), headers={'cookie': f'PSESSIONID={p_session_id}'})
            for mapping in parser.parse_mapping_on_page(res.text):
                mapping[f"full_name_{language_str.lower()}"] = mapping.pop("full_name")
                yield mapping
