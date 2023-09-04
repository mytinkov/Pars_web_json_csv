import requests
from bs4 import BeautifulSoup
import json
import csv

url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.35"
}
req = requests.get(url, headers=headers)
req.encoding = req.apparent_encoding  # Устанавливаем кодировку на основе автоматического определения
src = req.text
soup = BeautifulSoup(src, "lxml")
with open("index.html", "w", encoding="utf-8") as file:
    file.write(soup.prettify())

with open("index.html", encoding="utf-8") as file:
    src = file.read()
soup = BeautifulSoup(src, "lxml")

all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
all_categories_dict = {}

for item in all_products_hrefs:
    item_text = item.text
    item_href = "https://health-diet.ru" + item.get("href")
    all_categories_dict[item_text.strip().replace("\n","")] = item_href

with open("all_categories_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open("all_categories_dict.json", encoding='utf-8') as file:
    all_categories = json.load(file)

iteration_count = int(len(all_categories) - 1)
count = 0
print(f"Всего итераций: {iteration_count}")


for category_name, category_href in all_categories.items():
    rep = [' ', '-', ',', "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f"data/{count}_{category_name}.html", "w", encoding='utf-8') as file:
        file.write(src)

    with open(f"data/{count}_{category_name}.html", encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Проверяем наличие таблицы на странице
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # Собираем заголовки таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    products = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(
            (
                products,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )

    # Собираем данные продуктов:
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []
    for item in products_data:
        products_tds = item.find_all("td")
        title = products_tds[0].find("a").text
        calories = products_tds[1].text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        carbohydrates = products_tds[4].text

        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates
            }
        )

        with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

    with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8-sig") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"# Итерация {count}. {category_name} записан...")
    iteration_count -= 1

    if iteration_count == 0:
        print("Работа закончена")
        break

    print(f"Осталось итераций: {iteration_count}")
