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
        """
        Output: A dictionary of degrees, e.g.:
        {
            '12345': {
                'nr': '17 013',
                'full_name_en': '17 013 Master of Science in Informatik [20181]',
                'full_name_de': '...',
                'subtitle_en': '...',
                'subtitle_de': '...',
                'version': '2018'
            },
            ...
        }
        """
        # we need to manually iterate over all possible numbers since the module catalog doesn't contain all degrees
        for degree_id in range(0, 10000):
            res = requests.get(
                "https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
                f"pStpStpNr={degree_id}",
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
            english_degree = parser.parse_degree(res.text)
            res = requests.get(
                "https://campus.tum.de/tumonline/pl/ui/$ctx/wbstpcs.showSpoTree?"
                f"pStpStpNr={degree_id}",
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=False)}'})
            german_degree = parser.parse_degree(res.text)
            if not english_degree or not german_degree:
                continue
            yield degree_id, {
                "nr": english_degree["nr"],
                "full_name_en": english_degree["full_name"],
                "subtitle_en": english_degree["subtitle"],
                "full_name_de": german_degree["full_name"],
                "subtitle_de": german_degree["subtitle"],
                "version": english_degree["version"]
            }

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def modules(self) -> Iterator[str, str]:
        """
        Output: A list of tuples containing module ID, English name, and German name, e.g.:
        [
            ('98765', {
                'name_en': 'Introduction to Data Science',
                'name_de': 'Einführung in die Datenwissenschaft',
                'nr': 'IN0001'
            }),
            ...
        ]
        """
        res = requests.get(
            f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules',
            headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
        number_of_pages = parser.module_page_number(res.text)
        for page_index in range(number_of_pages):
            # get the modules on the current page
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules'
                f'&pPageNr={page_index + 1}&pSort=2',
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=True)}'})
            modules_en = parser.parse_modules_on_page(res.text)
            res = requests.get(
                f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules'
                f'&pPageNr={page_index + 1}&pSort=2',
                headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=False)}'})
            modules_de = parser.parse_modules_on_page(res.text)
            all_module_ids = modules_en.keys() | modules_de.keys()
            for module_id in all_module_ids:
                name_en, nr_en = modules_en.get(module_id, (None, None))
                name_de, nr_de = modules_de.get(module_id, (None, None))
                yield (module_id, {
                    "name_en": name_en,
                    "name_de": name_de,
                    "nr": nr_en if nr_en else nr_de
                })

    @retry(exceptions=RequestException, tries=10, delay=10, backoff=2)
    def module_degree_mappings(self, module_id: str) -> Iterator[str, dict]:
        """
        Output: A list of tuples containing degree ID and mapping information, e.g.:
        [
            ('12345', {
                'version': '20181',
                'ects': 6.0,
                'weighting_factor': 1.0,
                'valid_from': '2022S',
                'valid_to': None,
            }),
            ('67890', {
                'version': '20181',
                'ects': 6.0,
                'weighting_factor': 1.0,
                'valid_from': '2021W',
                'valid_to': '2022W'
            }),
            ...
        ]
        """

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
            mappings = parser.parse_mapping_on_page(res.text)
            for degree_id in mappings:
                yield (
                    degree_id,
                    mappings[degree_id]
                )
