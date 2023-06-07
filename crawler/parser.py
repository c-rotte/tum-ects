from bs4 import BeautifulSoup
import re

# ignore XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore")


def parse_degree(text: str) -> dict:
    """parses the degrees from the html response"""
    soup = BeautifulSoup(text, "lxml")
    if 'Curriculum Support' in soup.head.title.string:
        return None
    title = soup.find('span', {'title': 'Curriculum version '})
    if not title:
        title = soup.find('span', {'title': 'SPO-Version '})
    title = title.text
    subtitle = soup.find('td', {'class': 'pageOwner'}).span.text
    version = title.split('[')[1].split(']')[0] if '[' in title and ']' in title else None
    return {
        "nr": subtitle[0:6],
        "full_name": title,
        "subtitle": subtitle,
        "version": version
    }


def module_page_number(text: str) -> int:
    """parses the number of pages for the given module"""
    soup = BeautifulSoup(text, "lxml")
    # first, check if we have any modules
    if soup.find("tr", {"class": "cNoEntry"}):
        return 0
    # if we have modules, get the number of pages
    page_select = soup.find("select", {"name": "pPageNr"})
    return len(page_select.find_all("option"))


def parse_modules_on_page(text: str) -> dict:
    """parses the modules on the given page"""
    soup = BeautifulSoup(text, "lxml")
    table = soup.find("table", {"id": "idModHBTableORG"})
    result = {}
    for tr in table.find("tbody").find_all("tr"):
        td_list = tr.find_all("td", {"class": "bold L"})
        # get the module id and name
        a_list = td_list[0].find_all("a")
        href = a_list[1].get("href")
        if "pKnotenNr" not in href:
            continue
        module_name = a_list[1].text
        module_number = td_list[1].text
        module_id = href.split("pKnotenNr=")[1].split("&")[0]
        result[module_id] = {
            "name": module_name,
            "number": module_number
        }
    return result


def parse_module_info_tab_ids(text: str) -> dict:
    """parses the module info tab ids from the html response"""
    tab_ids = re.findall(r'registerTab\("[^"]*",\s*"(\d+)"', text)
    soup = BeautifulSoup(text, "lxml")
    result = {}
    for tab_id in tab_ids:
        tab_header = soup.find("a", {"id": tab_id})
        result[tab_id] = tab_header.text.strip()
    return result


def parse_module_info(text: str) -> dict:
    """parses the module info from the html response"""
    soup = BeautifulSoup(text, "lxml")
    fieldsets = soup.find_all("fieldset", {"id": "idPublicModuleDetailContainer"})
    result = {}
    for fieldset in fieldsets:
        version = fieldset.find("legend").find("span").text.strip()
        table = fieldset.find("table")
        entries = {}
        for tr in table.find_all("tr"):
            try:
                key = tr.find("td", {"class": "MaskRenderer MaskLabel"}).find("label").text.strip()
                value_table = tr.find("td", {"class": "MaskRenderer top"}).find_all("td", {"class": "MaskRenderer"})
                values = [value.text.strip() for value in value_table]
                entries[key] = values
            except:
                pass
        print(version, entries)

        def find_entry(keys: list) -> str:
            for key in keys:
                if key in entries:
                    return ",".join(entries[key])
            return None

        result[version] = {
            "level": find_entry(["Module Level", "Modulniveau"]),
            "abbreviation": find_entry(["Abbreviation", "Kürzel"]),
            "subtitle": find_entry(["Subtitle", "Untertitel"]),
            "duration": find_entry(["Duration", "Moduldauer"]),
            "occurence": find_entry(["Occurence", "Turnus"]),
            "language": find_entry(["Language", "Sprache"]),
            "related_programs": find_entry(["Related Programs", "Zugehörige Programme"]),
            "total_hours": find_entry(["Total Hours", "Gesamtstunden"]),
            "contact_hours": find_entry(["Contact Hours", "Präsenzstunden"]),
            "self_study_hours": find_entry(["Self Study", "Eigenstudiumstunden"]),
            "assessment_method": find_entry(
                ["Description of Achievement and Assessment Methods", "Beschreibung der Studien-/Prüfungsleistungen"]),
            "retake_next_semester": find_entry(["Exam retake next semester", "Prüfungswiederholung im Folgesemester"]),
            "retake_end_of_semester": find_entry(
                ["Exam retake at the end of semester", "Prüfungswiederholung am Semesterende"]),
            "prerequisites": find_entry(["Prerequisites (recommended)", "(Empfohlene) Voraussetzungen"]),
            "learning_outcomes": find_entry(["Intended Learning Outcomes", "Angestrebte Lernergebnisse"]),
            "content": find_entry(["Content", "Inhalt"]),
            "learning_methods": find_entry(["Teaching and Learning Methods", "Lehr- und Lernmethode"]),
            "media": find_entry(["Media", "Medienformen"]),
            "reading_list": find_entry(["Reading List", "Literatur"]),
            "responsible": find_entry(["Name(s)", "Name(n)"]),
        }
    return result


def mapping_page_number(text: str) -> int:
    """parses the number of pages for the given mapping"""
    soup = BeautifulSoup(text, "lxml")
    select = soup.find("td", {"class": "coTableNaviPageSelect"})
    if not select:
        return 1
    # if we have more than one page, get the number of pages
    pages_str = select.find("select").next_sibling.text.strip().replace("of ", "").replace("von ", "")
    return int(pages_str)


def parse_mapping_on_page(text: str) -> dict:
    """parses the mapping on the given page"""
    soup = BeautifulSoup(text, "lxml")
    tbody = soup.find("table", {"class": "cotable"}).find("tbody")
    result = {}
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
        # get the pStpStpNr
        degree_id = td_list[2].find("a").get("href").split("pStpStpNr=")[1].split("&")[0]
        result[degree_id] = {
            "version": names[2],
            "ects": float(names[5].replace(",", ".")) if names[5] else None,
            "weighting_factor": float(names[8].replace(",", ".")) if names[8] else None,
            "valid_from": names[11],
            "valid_to": names[12]
        }
    return result
