import unicodedata
from bs4 import BeautifulSoup
import bs4
import json


def parse_degree(text: str) -> dict:
    """parses the degrees from the html response"""
    soup = BeautifulSoup(text, "html.parser")
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
        result[module_id] = name
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
