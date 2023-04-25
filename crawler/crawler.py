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
    def degrees(self) -> dict:
        """returns a list of all degrees"""
        res = requests.get(
            "https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbShow?"
            "pOrgNr=1&pId=tabIdSPOModules_tabid&pTabContainerId=",
            headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
        english_degrees = parser.parse_degrees(res.text)
        for _, degree_info in english_degrees:
            degree_info["full_text_en"] = degree_info.pop("full_text")
            degree_info["short_text_en"] = degree_info.pop("short_text")
        res = requests.get(
            "https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbShow?"
            "pOrgNr=1&pId=tabIdSPOModules_tabid&pTabContainerId=",
            headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=False)}'})
        german_degrees = parser.parse_degrees(res.text)
        for _, degree_info in german_degrees:
            degree_info["full_text_de"] = degree_info.pop("full_text")
            degree_info["short_text_de"] = degree_info.pop("short_text")
        all_degree_ids = set().union(english_degrees.keys(), german_degrees.keys())
        return {
            # unionize english and german
            degree_id: dict(english_degrees.get(degree_id, {}), **german_degrees.get(degree_id, {}))
            for degree_id in all_degree_ids
        }

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def modules(self) -> Iterator[str, str]:
        """returns a list of all modules"""
        res = requests.get(
            f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules',
            headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
        number_of_pages = parser.module_page_number(res.text)
        for page_index in range(number_of_pages):
            # get the modules on the current page
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules&pPageNr={page_index + 1}',
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
            modules_en = parser.parse_modules_on_page(res.text)
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules&pPageNr={page_index + 1}',
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=False)}'})
            modules_de = parser.parse_modules_on_page(res.text)
            all_module_ids = set().union(modules_en.keys(), modules_en.keys())
            for module_id in all_module_ids:
                yield (
                    module_id,
                    modules_en.get(module_id, None),
                    modules_de.get(module_id, None)
                )

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def module_degree_mappings(self, module_id: str) -> Iterator[str, dict]:
        """returns a list of all degree programs containing the module"""

        def craft_url(page_nr=1, english=True):
            language_str = "EN" if english else "DE"
            url = ("https://campus.tum.de/tumonline/pl/ui/$ctx/wbModHB.cbUpdateCurrAssignmentTable?"
                   f"pOrgNr=1&pExtView=J&pKnotenNr={module_id}"
                   f"&pTableId=curr_assignment_table_{language_str}_{module_id}&"
                   f"pLangCode={language_str}&pExtFetching=J&pPageNr={page_nr}&pSort=&pFilter=")
            return url

        res = requests.get(craft_url(), headers={
            'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'
        })
        pages = parser.mapping_page_number(res.text)
        for page in range(pages):
            res = requests.get(craft_url(page + 1, english=True), headers={
                'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'
            })
            mappings_en = parser.parse_mapping_on_page(res.text)
            for degree_id in mappings_en:
                mappings_en[degree_id]["full_name_en"] = mappings_en[degree_id].pop("full_name")
            res = requests.get(craft_url(page + 1, english=False), headers={
                'cookie': f'PSESSIONID={self._get_p_session_id(english=False)}'
            })
            mappings_de = parser.parse_mapping_on_page(res.text)
            for degree_id in mappings_de:
                mappings_de[degree_id]["full_name_de"] = mappings_de[degree_id].pop("full_name")
            all_degree_ids = set().union(mappings_en.keys(), mappings_de.keys())
            for degree_id in all_degree_ids:
                yield (
                    degree_id,
                    dict(mappings_en.get(degree_id, {}), **mappings_de.get(degree_id, {}))
                )


crawler = Crawler()
degrees = set()
c = 0
for module_id, module_name_en, module_name_de in crawler.modules():
    print(f"module_name_en={module_name_en}, module_name_de={module_name_de}")
    for degree_id, mapping_info in crawler.module_degree_mappings(module_id):
        name = mapping_info["full_name_en"]
        if name[:12] not in degrees:
            print(mapping_info)
        degrees.add(name[:12])
    c += 1
print(len(degrees))
print(c)
