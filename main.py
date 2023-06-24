import re
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from driver import SeleniumDriver


ITEM_TYPE_MAP = {
    "Painted BM Decals": "Animated Decal",
    "Unpainted BM Decals": "Animated Decal",
    "Painted Goal Explosions": "Goal Explosion",
    "Painted Cars": "Body",
    "Painted Wheels [Exotic]": "Wheels",
    "Painted Wheels [Limited]": "Wheels",
    "Painted Wheels [Import]": "Wheels",
    "Painted Wheels [Very Rare]": "Wheels",
    "Painted Wheels [Rare]": "Wheels",
    "Painted Wheels [Uncommon]": "Wheels",
    "Painted Decals": "Decal",  # Might also be 'Animated Decal'
    "Painted Boosts": "Rocket Boost",
    "Painted Toppers": "Topper",
    "Painted Antennas": "Antenna",
    "Painted Trails": "Trail",
    "Painted Banners": "Player Banner",
    "Painted Avatar Borders": "Avatar Border",
    "Alpha + Beta": None,
    "Unpainted Goal Explosions": "Goal Expolosion",
    "Unpainted Cars": "Body",
    "Unpainted Wheels": "Wheels",
    "Unpainted Decals": "Decal",  # Might also be 'Animated Decal'
    "Unpainted Boosts": "Rocket Boost",
    "Unpainted Toppers": "Topper",
    "Unpainted Antennas": "Antenna",
    "Unpainted Trails": "Trail",
    "Unpainted Banners": "Player Banner",
    "Unpainted Avatar Borders": "Avatar Border",
    "Engine Audio": "Engine Audio",
    "Gift Packs": "Reward Item",
    "Paint Finishes": "Paint Finish",
}


def string_price_to_int(price: str) -> float:
    """Map item prices from string to float

    :param price: price as a string
    :return: the average price as a float
    """
    price = price.replace("\u200a-\u200a", "-").replace("—", "0").strip()

    if not price:
        return 0.0

    p = re.findall(r"\d+(?:\.\d+)?", price)
    p = list(map(float, p))
    if len(p) == 1:
        if p[0] == 0.0:
            return 0.0
    return (p[0] + p[1]) * 1000 / 2 if "k" in price else (p[0] + p[1]) / 2


def get_data(blueprint: bool = False) -> BeautifulSoup:
    """Scrap rocket league item prices

    :param blueprint: True for blueprint item values, False otherwise
    :return: The HTML page as nested data structure (a BeautifulSoup object)
    """
    driver = SeleniumDriver()
    result = driver.get_html(blueprint=blueprint)
    # print(r)
    with open(
        "rlinsider.pkl", "wb"
    ) as file:  # "wb" because we want to write in binary mode
        pickle.dump(result, file)
    driver.close()

    # Open stored rl.insider HTML
    with open(
        "rlinsider.pkl", "rb"
    ) as file:  # "rb" because we want to read in binary mode
        html = pickle.load(file)
    return BeautifulSoup(html, "html.parser")


def get_colours(soup: BeautifulSoup):
    """Get a list of available item colours

    :param soup: the rl.insider.gg price page html as a BeautifulSoup object
    :return: list of colours (strings)
    """
    color_labels = soup.find("table", {"id": "colorLabels"})
    colors = color_labels.find_all("span", {"class": "priceTableHeader"})  # type: ignore
    colors = [color.text for color in colors]
    return colors


def extract_prices(soup: BeautifulSoup, color_list: list[str]) -> list[list[str]]:
    """Extract the prices of all items and their painted versions from the HTML page

    :param color_list: list of item colours (as strings)
    :param soup: the rl.insider.gg price page html as a BeautifulSoup object
    :return: a matrix (list of lists) of the items and their prices
    """
    price_list = []
    # Get all price tables from the HTML
    price_containers = soup.find_all("div", {"class": "priceTableContainer"})

    # For each price table
    for price_container in price_containers:
        # Get the table name (ie item type)
        header = price_container.find_all("h2")
        # Get all items in the table
        items = price_container.find_all("tr")
        for item in items:
            # Get all painted price values
            prices = item.find_all("td")
            if prices:
                name = prices[0].find("div", {"class": "fnl"}).text
                if "Painted" in header[0].text:
                    prices = [string_price_to_int(price.text) for price in prices[1:]]
                else:
                    prices = [string_price_to_int(prices[1].text)] + [0] * (
                        len(color_list) - 1
                    )
                row = [name, ITEM_TYPE_MAP[header[0].text]] + prices
                # print(row)
                price_list.append(row)

    return price_list


def load_inventory(blueprint: bool) -> pd.DataFrame:
    """Import the item inventory list

    :param blueprint: True for blueprint item values, False otherwise
    :return: the item inventory as dataframe
    """
    # Load and preprocess rocket league inventory
    inventory = pd.read_csv(
        "inventory.csv", encoding="windows-1252", on_bad_lines="skip"
    )
    inventory = inventory[inventory.tradeable != "False"]
    inventory["paint"].replace(["none"], "Default", inplace=True)
    inventory["paint"].replace(["Titanium White"], "White", inplace=True)
    inventory["paint"].replace(["Forest Green"], "Green", inplace=True)
    inventory["paint"].replace(["Burnt Sienna"], "Sienna", inplace=True)
    inventory = (
        inventory[inventory.slot != "Blueprint"]
        if not blueprint
        else inventory[inventory.slot == "Blueprint"]
    )
    return inventory


def get_item_prices(
    price_list: list[list[str]], inventory: pd.DataFrame, colour_list: list[str]
) -> None:
    """Combine item prices with the inventory items to find the most valuable items (from the inventory)

    :param price_list: list of prices (price per colour variant) for each item
    :param inventory: a dataframe of inventory items
    :param colour_list: list of item colours (as strings)
    :return: Nothing (print the 20 most valuable items)
    """
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)

    price_df = pd.DataFrame(price_list, columns=["Name", "Type"] + colour_list)
    combined = inventory.merge(price_df, left_on="name", right_on="Name")
    combined["price"] = combined.apply(lambda x: x[x["paint"]], axis=1)

    out = combined[["name", "slot", "paint", "price"]]
    out = out.sort_values(by=["price"], ascending=False)
    print(out.head(n=20))


def run() -> None:
    """Main program logic

    :return: Nothing
    """
    blueprint = False
    soup = get_data(blueprint)
    colours = get_colours(soup)
    prices = extract_prices(soup, colours)
    inventory = load_inventory(blueprint)
    get_item_prices(prices, inventory, colours)


if __name__ == "__main__":
    run()
