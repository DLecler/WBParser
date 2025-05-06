import json
import os
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# from logger_config import logger

# Глобальные переменные
request_count = 0
result_data = []
result_max_size = 30000

result_products = 0
result_max_products = 50

result_size = 0
result_prefix = 0
result_pref = {}

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
сategories_and_childs_path = os.path.join(project_root, 'Data', 'Categories_and_childs.json')

poepota = ("dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&uclusters=3&uiv=0&"
           "uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-"
           "9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_"
           "U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-"
           "W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular")


def create_session():
    """Создает и возвращает сессию requests с настройками повторных попыток."""
    session = Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429], allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def send_request(url):
    """Отправляет GET-запрос и обрабатывает ошибки."""
    global request_count
    session = create_session()
    try:
        request_count += 1
        # logger.info(f"GET: {url}")
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # logger.error(f"Ошибка при запросе {url}: {e}")
        return None

def increment_key(key):
    if key in result_pref:
        result_pref[key] += 1  # Если ключ существует, увеличиваем значение на 1
    else:
        result_pref[key] = 0  # Если ключа нет, добавляем его со значением 1

def write_result_file(parents_names):
    """Записывает собранные данные в JSON-файл."""
    global result_data, result_prefix, result_size
    global result_products

    if not result_data:
        return

    directory_path = "results_parse"
    os.makedirs(directory_path, exist_ok=True)

    # file_name = f"result_parse-{resultFilename}-{result_prefix}.json"
    file_name = f"result_parse-{parents_names}-{result_pref[parents_names]}.json"

    # file_name = f"result_parse-{result_prefix}.json"
    file_route = os.path.join(directory_path, file_name)

    with open(file_route, 'w', encoding='utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)



    # result_prefix += 1
    result_pref[parents_names] += 1
    # result_size = 0

    result_products = 0

    result_data = []  # Очищаем список для новых данных

def find_category_with_children(path: str, category_id: int) -> str:
    """
    Загружает JSON-файл и рекурсивно ищет категорию по точному совпадению ID.
    Возвращает список с подкатегориями найденной категории в формате JSON или пустой список, если не найдено.
    """

    def recursive_search(categories, target_id):
        for category in categories:
            if category.get("id") == target_id:
                if category.get("childs"):
                    return category.get("childs", [])
                else:
                    return [category]

            if "childs" in category:
                result = recursive_search(category["childs"], target_id)
                if result:
                    return result
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        result = recursive_search(data, category_id)
        return json.dumps(result, ensure_ascii=False, indent=4)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки файла: {e}")
        return json.dumps([])

# def find_category_with_children(filename: str, category_id: int) -> str:
#     """
#     Загружает JSON-файл и рекурсивно ищет категорию по точному совпадению ID.
#     Возвращает список с подкатегориями найденной категории в формате JSON или пустой список, если не найдено.
#     """
#
#     def recursive_search(categories, target_id):
#         for category in categories:
#
#             if category.get("id") == target_id:
#                 if category.get("childs"):
#                     return category.get("childs", [])
#                 else:
#                     return [category]
#
#             if "childs" in category:
#                 result = recursive_search(category["childs"], target_id)
#                 if result:
#                     return result
#         return []
#
#     try:
#         with open(filename, "r", encoding="utf-8") as file:
#             data = json.load(file)
#
#         result = recursive_search(data, category_id)
#         return json.dumps(result, ensure_ascii=False, indent=4)
#     except (FileNotFoundError, json.JSONDecodeError) as e:
#         print(f"Ошибка загрузки файла: {e}")
#         return json.dumps([])


def process_products(products, prod, parents_names):
    """Обрабатывает список товаров и сохраняет в result_data."""
    global result_data, result_max_size, result_size
    global result_products

    for product in products:
        # result_data.append({
        #     "id": product.get("id"),
        #     "name": product.get("name"),
        #     "brand": product.get("brand"),
        #     "brandId": product.get("brandId"),
        #     "subjectId": product.get("subjectId"),
        #     "supplier": product.get("supplier"),
        #     "supplierId": product.get("supplierId"),
        #
        #     "colors_name": [color.get("name") for color in product.get("colors", [])],
        #     "supplierRating": product.get("supplierRating"),
        #     "rating": product.get("rating"),
        #     "reviewRating": product.get("reviewRating"),
        #     "nmReviewRating": product.get("nmReviewRating"),
        #     "feedbacks": product.get("feedbacks"),
        #     "totalQuantity": product.get("totalQuantity"),
        #
        #     "basic": product.get("sizes", [{}])[0].get("price", {}).get("basic", "None"),
        #     "product": product.get("sizes", [{}])[0].get("price", {}).get("product", "None"),
        #     "total": product.get("sizes", [{}])[0].get("price", {}).get("total", "None"),
        #     "logistics": product.get("sizes", [{}])[0].get("price", {}).get("logistics", "None"),
        # })

        # if len(result_data) >= result_max_size:
        #     write_result_file()

        # result_data.append(product)
        # result_size += len(product.keys())
        # if result_size >= result_max_size:
        #     write_result_file(parents_names)

        result_data.append(product)
        result_products += 1
        if result_products >= result_max_products:
            write_result_file(parents_names)


# def get_products(list_catalog):
def get_products(list_catalog, sumPages, breakPage, resultFilename, req, prod):
    """Собирает данные о товарах по категориям."""

    global result_data

    url1 = "https://catalog.wb.ru/catalog/"
    url2 = "/v2/catalog?"

    for catalog in list_catalog:
        name = catalog.get("name")
        shard = catalog.get("shard")
        query = catalog.get("query")
        childs = catalog.get("childs", [])

        # logger.debug(f"Обработка категории: {name}, {shard=}, {query=}")
        # print(f"Обработка категории: {name}, {shard=}, {query=}")

        page = 0
        while True:

            page += 1

            sumPages += 1
            if sumPages > breakPage:
                break

            print(f"Обработка категории: {name}, {shard=}, {query=}")

            if req == "all":
                request_url = f"{url1}{shard}{url2}{query}&page={page}&{poepota}"
            else:
                request_url = f"{url1}{shard}{url2}{query}&page={page}&{poepota}&{req}"
            data = send_request(request_url)
            # print(f"Отправлен ЗАПРОС {request_url}: {resultFilename} _ {prod}")

            # print("|||||||||")
            # print(data)
            # print("|||||||||")

            if not data or "data" not in data:
                # logger.error(f"Ошибка загрузки товаров: {name}, {page=}")
                break

            products = data.get("data", {}).get("products", [])
            if not products:
                break  # Если товаров нет, прекращаем запросы
            process_products(products, prod, resultFilename)

        # Рекурсивно обрабатываем подкатегории
        if childs:
            get_products(childs, sumPages, breakPage, resultFilename, req, prod)

def load_json(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Ошибка чтения файла] {filepath}: {e}")
        return None

def start_parse(allRequests, breakPage):
    global сategories_and_childs_path, result_pref
    result = []

    def get_full_parent_chain_by_id(path: str, category_id: int) -> str | None:
        def find_category(data, target_id):
            for item in data:
                if item.get("id") == target_id:
                    return item
                if "childs" in item:
                    found = find_category(item["childs"], target_id)
                    if found:
                        return found
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            current = find_category(data, category_id)
            if not current:
                return None

            parent_chain = [current["name"]]  # Сначала добавляем текущую категорию

            # Рекурсивно идем по родителям, пока не дойдем до самого верхнего
            while current.get("parent") is not None:
                parent = find_category(data, current["parent"])
                if not parent:
                    break
                parent_chain.insert(0, parent["name"])  # Вставляем родителя в начало списка
                current = parent

            return "_".join(parent_chain)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка чтения файла: {e}")
            return None

    for item in allRequests:
        parts = item.split('&')
        prod = None
        xsubname = None
        rest = []

        for part in parts:
            if part.startswith('prod='):
                prod = int(part.split('=')[1])
            elif part.startswith('xsubname='):
                xsubname = part.split('=')[1]  # сохраняем, но не добавляем в rest
            else:
                rest.append(part)

        request = '&'.join(rest) if rest else "all"
        result.append({prod, request})

        category = find_category_with_children(сategories_and_childs_path, prod)
        names_parents = get_full_parent_chain_by_id(сategories_and_childs_path, prod)

        if xsubname is not None:
            names_parents = names_parents + "_" + xsubname
        if names_parents not in result_pref:

            result_pref[names_parents] = 1
        print(f"------------------\nРодительский путь: {names_parents}, prod: {prod}, request: {request}")
        # get_products(json.loads(category), 0, breakPage, names_parents, request, prod)
        # write_result_file(names_parents)



# def start_parse(allRequests, breakPage):
#
#     global сategories_and_childs_path
#     result = []
#
#     for item in allRequests:
#         parts = item.split('&')
#         prod = None
#         rest = []
#
#         for part in parts:
#             if part.startswith('prod='):
#                 prod = int(part.split('=')[1])
#             else:
#                 rest.append(part)
#
#         # print(f'=== {prod}')
#         request = '&'.join(rest) if rest else "all"
#         # print(f'+++ {request}')
#         result.append({prod, request})
#
#         print("------------------")
#         category = find_category_with_children(сategories_and_childs_path, prod)
#         get_products(json.loads(category), request, 0, breakPage)
#         write_result_file()
#         # print(category)
#
#     # print()
#     # # Вывод результата
#     # for r in result:
#     #     print(r)
#
#     # category = find_category_with_children("Data/Categories_and_childs.json", prod)
#     # print(category)
#     # get_products(json.loads(category))
#     # write_result_file()