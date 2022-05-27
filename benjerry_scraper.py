from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def make_soup(url):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url)
    return BeautifulSoup(response.text, "html.parser")


def make_flavor_directory(soup):
    flavor_info = soup.find_all(class_="landing-item")

    flavor_directory = {}

    for flavor in flavor_info:
        name = flavor.attrs["data-pname"].replace("\u200b", "")
        new = flavor.find(class_="new-product") != None
        link = "https://www.benandjerrys.ca" + flavor.attrs["data-producturl"]

        flavor_directory[name] = {"Link": link, "New": new}
    return flavor_directory


def make_ingredient_list(content):
    ingredients = content[1].text.split(",")

    concat_index = [[]]
    ci = 0

    for i, ingredient in enumerate(ingredients):

        if ("(" in ingredient) and (")" in ingredient):
            pass

        elif ("(" in ingredient) or (")" in ingredient):
            if len(concat_index[ci]) == 2:
                concat_index.append([])
                ci += 1
            concat_index[ci].append(i)

    if len(concat_index[0]) != 0:

        for pair in concat_index[::-1]:
            concat_ingr = ingredients[pair[0]] + "," + ingredients[pair[1]]
            ingredients.pop(pair[1])
            ingredients.pop(pair[0])
            ingredients.insert(pair[0], concat_ingr)

    for i, ingredient in enumerate(ingredients):
        ingredients[i] = ingredient.strip().replace(".", "")

    return ingredients


def write_to_txt(dict):
    f = open("ben_and_jerry_flavors.txt", "w")
    f.write(str(dict))
    f.close()


def scrape_bnj():
    url = "https://www.benandjerrys.ca"
    category = "/en/flavours/ice-cream-pints"

    print("attempting to make soup....")

    soup = make_soup(url + category)

    print("soup created!")

    print("making flavor directory...")

    flavor_directory = make_flavor_directory(soup)

    print("flavor directory created!")

    print("starting flavor loop...")
    for flavor in flavor_directory:

        print("creating soup for", flavor, "...")

        print("flavor url: ", flavor_directory[flavor]["Link"])
        soup = make_soup(flavor_directory[flavor]["Link"])
        print(flavor, "soup created!")

        content = list(soup.find(class_="accordion-content-style").children)

        flavor_directory[flavor]["Nutrition Facts img"] = (
            url + content[5].attrs["data-original"]
        )
        print("added Nutrition Facts img to", flavor, "directory!")

        flavor_directory[flavor]["Ingredients"] = make_ingredient_list(content)
        print("added Ingredients list to", flavor, "directory!")

        flavor_directory[flavor]["Allergy Info"] = (
            content[3]
            .text.replace("\n", "")
            .replace("\t", "")
            .replace("Allergy Information: Allergen Information: CONTAINS ", "")
            .replace("Allergy Information: ", "")
            .replace(".", "")
            .replace(" AND", "")
            .split(",")
        )
        print("added Allergy Info to", flavor, "directory!")

    print("writing to txt...")
    write_to_txt(flavor_directory)
    print("txt created!!")

    return flavor_directory


if __name__ == "__main__":
    scrape_bnj()
