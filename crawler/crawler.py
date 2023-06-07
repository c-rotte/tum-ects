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
    def modules(self) -> Iterator[str, dict]:
        """
        Output: A list of tuples containing module ID, label, and information e.g.:
        [
            ('98765', {
                'title': 'Software Engineering for Business Applications',
                'number': 'IN0001',
                'information_en': {
                    'SS23' : {
                        'level': 'Module Level',
                        'abbreviation': 'Abbreviation',
                        'subtitle': 'Subtitle',
                        'duration': 'Duration',
                        'occurence': 'Occurence',
                        'language': 'Language',
                        'related_programs': 'Related Programs',
                        'work_load': 'Total Hours',
                        'contact_hours': 'Contact Hours',
                        'self_study_hours': 'Self Study Hours',
                        'assessment_method': 'Description of Achievement and Assessment Methods',
                        'retake_next_semester': 'Exam retake next semester',
                        'retake_end_of_semester': 'Exam retake at the end of semester',
                        'prerequisites': 'Prerequisites (recommended)',
                        'learning_outcomes': 'Intended Learning Outcomes',
                        'content': 'Content',
                        'learning_methods': 'Teaching and Learning Methods',
                        'media': 'Media',
                        'reading_list': 'Reading List',
                        'responsibility': 'Name(s)',
                    },
                    ...
                },
                'information_de': {
                    ...
                }
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
            modules = {}
            for english in [True, False]:
                res = requests.get(
                    f'{self.url_base}/WBMODHB.cbShowMHBListe?pCaller=tabIdOrgModules'
                    f'&pPageNr={page_index + 1}&pSort=2',
                    headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=english)}'})
                modules = modules | parser.parse_modules_on_page(res.text)
            for module_id, (module_name, module_number) in modules.items():
                def get_module_information(english: bool) -> Iterator[str, dict]:
                    lanugage_label = 'EN' if english else 'DE'
                    res = requests.get(
                        f'{self.url_base}/WBMODHB.wbShowMHBReadOnly?pKnotenNr={module_id}',
                        headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=english)}'})
                    tab_ids = parser.parse_module_info_tab_ids(res.text)
                    for tab_id, tab_name in tab_ids.items():
                        res = requests.get(
                            f'{self.url_base}/wbModHB.cbLoadMHBTab?pKnotenNr={module_id}&pId={tab_id}'
                            f'&pLanguage={lanugage_label}&pOrgNr=&pTabContainerId=',
                            headers={'cookie': f'PSESSIONID={self._get_p_session_id(english=english)}'})
                        yield tab_name, parser.parse_module_info(res.text)

                english_module_info = {
                    tab_name: module_info for tab_name, module_info in get_module_information(english=True)
                }
                german_module_info = {
                    tab_name: module_info for tab_name, module_info in get_module_information(english=False)
                }

                yield module_id, {
                    "title": module_name,
                    "number": module_number,
                    "information_en": english_module_info,
                    "information_de": german_module_info
                }

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
