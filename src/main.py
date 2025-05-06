# uvicorn src.main:app --reload
from collections import defaultdict
from urllib.parse import urlencode, parse_qsl
from collections import defaultdict
from urllib.parse import parse_qs, urlencode

from src.parse_data import start_parse

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json

from collections import defaultdict
from urllib.parse import parse_qs, urlencode, unquote
import os, json
from urllib.parse import quote

from pydantic import BaseModel

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
сategories_and_childs_clear_path = os.path.join(project_root, 'Data', 'Categories_and_childs_clear.json')

selected_ids_storage = [...]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def redirect_to_login():
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "qqq":
        return RedirectResponse("/admin", status_code=303)
    return RedirectResponse("/user", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/admin")
async def redirect_to_categories():
    return RedirectResponse("/categories", status_code=303)

@app.get("/categories", response_class=HTMLResponse)
async def get_categories(request: Request):
    global сategories_and_childs_clear_path
    # file_path = os.path.join("static", "Categories_and_childs_clear.json")
    # with open(file_path, "r", encoding="utf-8") as file:
    with open(сategories_and_childs_clear_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # передаем данные для отображения в шаблоне
    return templates.TemplateResponse("categories.html", {"request": request, "categories": data})

def load_json(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Ошибка чтения файла] {filepath}: {e}")
        return None

def find_name_by_id(target_id: int) -> str:
    global сategories_and_childs_clear_path
    # path = os.path.join("static", "Categories_and_childs_clear.json")
    # data = load_json(path)

    data = load_json(сategories_and_childs_clear_path)

    def search_recursive(categories):
        for category in categories:
            if category.get("id") == target_id:
                return category.get("name")
            children = category.get("childs", [])
            result = search_recursive(children)
            if result:
                return result
        return None

    # print(search_recursive(data))
    return search_recursive(data)


@app.post("/categories")
async def receive_selected_ids(request: Request):
    global selected_ids_storage
    req_data = await request.json()
    ids = req_data.get("ids", [])
    selected_ids_storage = ids
    print("Получены ID категорий:", ids)
    print(f"{len(ids)} ID получены")
    return RedirectResponse(url="/parametres", status_code=303)


@app.get("/parametres")
async def show_parameters(request: Request):
    category_items = []

    for category_id in selected_ids_storage:
        name = find_name_by_id(int(category_id))
        if not name:
            print("Имя по ID не нашлось")
            continue

        parameters = []

        file_path = os.path.join("static", f"{name}.json")
        extra_file_path = os.path.join("static", f"{name}brands_suppliers.json")

        if os.path.exists(file_path):
            data = load_json(file_path)

            if isinstance(data, list):
                subcategory_names = []
                subcategory_params = []

                for sub in data:
                    sub_id = sub.get("id")
                    sub_name = sub.get("name")
                    if not sub_name:
                        continue
                    subcategory_names.append(sub_name)

                    sub_filters = sub.get("filters", [])
                    sub_params = []

                    for f in sub_filters:
                        param_id = f.get("id")
                        if param_id == None:
                            param_id = f.get("key")
                            # print(param_id)
                        param_name = f.get("name")
                        if not param_name:
                            continue
                        param_type = f.get("type", "list")
                        param = {
                            "id": param_id,  # Добавляем ID
                            "name": param_name,
                            "type": param_type
                        }

                        if param_name == "Цена":
                            min_price = f.get("minPriceU")
                            max_price = f.get("maxPriceU")
                            if min_price is not None and max_price is not None:
                                param["minPriceU"] = round(min_price / 100)
                                param["maxPriceU"] = round(max_price / 100)


                        items = f.get("items", [])
                        param["values"] = [
                            {
                                "id": item.get("id"),
                                "name": item.get("name")
                            }
                            for item in items
                            if item.get("name")
                        ]

                        sub_params.append(param)

                    subcategory_params.append({
                        "sub_category_id": sub_id,
                        "sub_category_name": sub_name,
                        "parameters": sub_params
                    })

                parameters.append({
                    "category_id": category_id,
                    "name": "Категория",
                    "type": "list",
                    "sub_parameters": subcategory_params
                })

            elif isinstance(data, dict):
                filters = data.get("filters", [])

                for f in filters:
                    param_id = f.get("id")  # ID параметра
                    if param_id == None:
                        param_id = f.get("key")
                        # print(param_id)
                    param_name = f.get("name")
                    if not param_name:
                        continue

                    param_type = f.get("type", "list")
                    param = {
                        "id": param_id,  # Добавляем ID
                        "name": param_name,
                        "type": param_type
                    }

                    if param_name == "Цена":
                        min_price = f.get("minPriceU")
                        max_price = f.get("maxPriceU")
                        if min_price is not None and max_price is not None:
                            param["minPriceU"] = round(min_price / 100)
                            param["maxPriceU"] = round(max_price / 100)

                    if param_type != "toggle":
                        items = f.get("items", [])
                        param["values"] = [
                            {
                                "id": item.get("id"),  # ID значения
                                "name": item.get("name")
                            }
                            for item in items
                            if item.get("name")
                        ]

                    parameters.append(param)

        if os.path.exists(extra_file_path):
            extra_data = load_json(extra_file_path)

            for obj in extra_data:
                if obj.get("id") == int(category_id):
                    for f in obj.get("filters", []):
                        if f.get("name") in ["Бренд", "Продавец"]:
                            param = {
                                # "id": f.get("id"),  # ID параметра
                                "id": f.get("key"),
                                "name": f.get("name"),
                                "items": [
                                    {
                                        "id": item.get("id"),  # ID значения
                                        "name": item.get("name")
                                    }
                                    for item in f.get("items", [])
                                    if item.get("name")
                                ]
                            }
                            parameters.append(param)

        category_items.append({
            "id": category_id,
            "name": name,
            "parameters": parameters
        })

    return templates.TemplateResponse("parametres.html", {
        "request": request,
        "category_items": category_items
    })


# Пример модели запроса
class PriceRange(BaseModel):
    min: int
    max: int

class ParametresPayload(BaseModel):
    activeKeys: list[str]
    prices: dict[str, PriceRange]


# @app.post("/parametres")
# async def get_parametres(payload: ParametresPayload):
#
#     # final = [
#     #     "prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&fpremiumuser=1&fdlvr=4%3B24&priceU=100%253B200&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677",
#     #     "prod=9835&xsubject=1889&faction=1&fnds=1&fdlvr=24%3B120&frating=1&foriginal=1&fpremium=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&priceU=500%253B600&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677",
#     #     "prod=15692",
#     #     "prod=9835&xsubject=600"
#     # ]
#
#     final = [
#         "prod=4830",
#         "prod=15692",
#         "prod=9835&xsubname=FM-трансмиттер&xsubject=764&fpremium=1&fpremiumuser=1&fdlvr=72&priceU=100%3B2000000",
#         "prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&fbrand=10987&frating=1&foriginal=1&f14081=409116%3B97230",
#         "prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&fbrand=27920%3B9546&fpremiumuser=1&fsupplier=33762&f11461=22528%3B22533",
#         "prod=9835&xsubname=Видеорегистратор автомобильный&xsubject=600"
#     ]
#
#     start_parse(final, 1)
#
#
#     return
#     # return final
































# def transform_input(arr):
#     result = []
#
#     # Шаг 1: Очистка и замены
#     cleaned = []
#     replacements = {
#         "fdlvr=2-4 часа": "fdlvr=4",
#         "fdlvr=Сегодня": "fdlvr=12",
#         "fdlvr=Завтра": "fdlvr=24",
#         "fdlvr=Послезавтра": "fdlvr=48",
#         "fdlvr=До 3 дней": "fdlvr=72",
#         "fdlvr=До 5 дней": "fdlvr=120"
#     }
#
#     for s in arr:
#         s = s.replace("param=", "").replace("&value", "")
#         if "fdlvr=Любой" in s:
#             continue
#         for old, new in replacements.items():
#             s = s.replace(old, new)
#         cleaned.append(s)
#
#     # Шаг 2: Добавление =1 к булевым параметрам
#     bool_params = {
#         "faction", "fnds", "frating", "foriginal",
#         "fpremium", "ffeedbackpoints", "fpremiumuser"
#     }
#
#     temp_map = defaultdict(lambda: defaultdict(list))
#     flat_map = defaultdict(lambda: defaultdict(list))
#
#     for s in cleaned:
#         parts = s.split("&")
#         param_map = {}
#         for p in parts:
#             key, val = p.split("=")
#             param_map[key] = val
#
#         prod = param_map.get("prod")
#         xsubject = param_map.get("xsubject")
#
#         keys = sorted(param_map.keys())
#
#         param_name = None
#         param_value = None
#
#         for k in keys:
#             if k not in ("prod", "xsubject", "priceU"):
#                 param_name = k
#                 param_value = param_map[k]
#                 break
#
#         # Обработка priceU — сохраняем как есть
#         if "priceU" in param_map:
#             flat_map[(prod, xsubject)]["priceU"].append(param_map["priceU"])
#             continue
#
#         # fdlvr — особый случай, каждый отдельно
#         if param_name == "fdlvr":
#             result.append(
#                 f"prod={prod}" +
#                 (f"&xsubject={xsubject}" if xsubject else "") +
#                 f"&fdlvr={param_value}"
#             )
#             continue
#
#         if param_name == "priceU":
#             result.append(
#                 f"prod={prod}" +
#                 (f"&xsubject={xsubject}" if xsubject else "") +
#                 f"&priceU={param_value}"
#             )
#             continue
#
#         # Добавить =1 к булевым
#         if param_name in bool_params:
#             result.append(
#                 f"prod={prod}" +
#                 (f"&xsubject={xsubject}" if xsubject else "") +
#                 f"&{param_name}=1"
#             )
#             continue
#
#         # Сбор для объединения (по prod + xsubject или prod)
#         if xsubject:
#             temp_map[(prod, xsubject)][param_name].append(param_value)
#         else:
#             flat_map[(prod, None)][param_name].append(param_value)
#
#     # Шаг 3: Объединение значений
#     for (prod, xsubject), param_dict in temp_map.items():
#         for param, values in param_dict.items():
#             if values[0] is not None:
#                 joined_vals = "%3B".join(values)
#                 line = f"prod={prod}&xsubject={xsubject}&{param}={joined_vals}"
#                 result.append(line)
#
#     for (prod, xsubject), param_dict in flat_map.items():
#         for param, values in param_dict.items():
#             print(f'prod = {prod}\nxsubject = {xsubject}\nparam = {param}\nvalues = {values}\n\n')
#             if values[0] is not None:
#                 joined_vals = "%3B".join(values)
#                 line = f"prod={prod}" + (f"&xsubject={xsubject}" if xsubject else "") + f"&{param}={joined_vals}"
#                 result.append(line)
#
#     print(f'transform_input\n{result}')
#
#     return result
#
#
# def group_query_params(dat):
#     data = transform_input(dat)
#     grouped = defaultdict(list)
#     brand_supplier_map = defaultdict(list)
#     brand_supplier_lines = defaultdict(dict)
#     untouched_lines = []
#
#     for line in data:
#         query = parse_qs(line)
#         prod = query.get('prod', [None])[0]
#         xsubject = query.get('xsubject', [None])[0]
#         key = (prod, xsubject)
#
#         # fdlvr и priceU — сохраняем как есть
#         if "fdlvr=" in line or "priceU=" in line:
#             untouched_lines.append(line)
#             continue
#
#         # fbrand/fsupplier — сохраняем отдельно
#         if "fbrand=" in line or "fsupplier=" in line:
#             if "fbrand=" in line:
#                 brand_supplier_lines[key]["fbrand"] = '&'.join(
#                     p for p in line.split('&') if p.startswith('fbrand='))
#             if "fsupplier=" in line:
#                 brand_supplier_lines[key]["fsupplier"] = '&'.join(
#                     p for p in line.split('&') if p.startswith('fsupplier='))
#             continue
#
#         # Прочие строки — группируем
#         param_part = '&'.join(
#             p for p in line.split('&')
#             if not p.startswith('prod=') and not p.startswith('xsubject=')
#         )
#         grouped[key].append(param_part)
#
#     # Формируем результат
#     result = []
#
#     # 1. Добавляем fbrand и fsupplier для каждой группы
#     for (prod, xsubject), params in brand_supplier_lines.items():
#         combined = [f'prod={prod}']
#         if xsubject:
#             combined.append(f'xsubject={xsubject}')
#         if 'fbrand' in params:
#             combined.append(params['fbrand'])
#         if 'fsupplier' in params:
#             combined.append(params['fsupplier'])
#         result.append('&'.join(combined))
#
#         # Сохраняем для добавления к другим строкам
#         brand_supplier_map[(prod, xsubject)] = []
#         if 'fbrand' in params:
#             brand_supplier_map[(prod, xsubject)].append(params['fbrand'])
#         if 'fsupplier' in params:
#             brand_supplier_map[(prod, xsubject)].append(params['fsupplier'])
#
#     # 2. Добавляем объединённые строки по другим параметрам
#     for (prod, xsubject), params in grouped.items():
#         prefix = f'prod={prod}'
#         if xsubject:
#             prefix += f'&xsubject={xsubject}'
#         extra = brand_supplier_map.get((prod, xsubject), [])
#         combined = '&'.join(params + extra)
#         result.append(f'{prefix}&{combined}' if combined else prefix)
#
#     # 3. Добавляем нетронутые строки (fdlvr и priceU)
#     result.extend(untouched_lines)
#
#     print(f'group_query_params\n{result}')
#
#     return expand_brand_supplier(result)
#
#
# def expand_brand_supplier(lines):
#     brand_supplier_by_prod = defaultdict(list)
#     removable_lines_by_prod = defaultdict(set)
#
#     # Шаг 1: собираем fbrand/fsupplier по prod
#     for i, line in enumerate(lines):
#         query = parse_qs(line)
#         prod = query.get('prod', [None])[0]
#         has_brand = 'fbrand' in query
#         has_supplier = 'fsupplier' in query
#         only_brand_or_supplier = all(k in {'prod', 'xsubject', 'fbrand', 'fsupplier'} for k in query)
#
#         if prod and (has_brand or has_supplier):
#             parts = []
#             if has_brand:
#                 for val in query['fbrand']:
#                     parts.append(('fbrand', val))
#             if has_supplier:
#                 for val in query['fsupplier']:
#                     parts.append(('fsupplier', val))
#             brand_supplier_by_prod[prod].extend(parts)
#
#             if only_brand_or_supplier:
#                 removable_lines_by_prod[prod].add(i)
#
#     used_prod_ids = set()
#     updated_lines = []
#
#     # Шаг 2: добавляем fbrand/fsupplier в строки без fdlvr/priceU
#     for i, line in enumerate(lines):
#         if i in [i for ids in removable_lines_by_prod.values() for i in ids]:
#             continue  # временно пропускаем, обработаем позже
#
#         if 'fdlvr=' in line or 'priceU=' in line:
#             updated_lines.append(line)
#             continue
#
#         query = parse_qs(line)
#         prod = query.get('prod', [None])[0]
#
#         if prod and prod in brand_supplier_by_prod:
#             existing_keys = set(query.keys())
#             additions_made = False
#             for k, v in brand_supplier_by_prod[prod]:
#                 if k not in existing_keys:
#                     query[k] = [v]
#                     additions_made = True
#             if additions_made:
#                 used_prod_ids.add(prod)
#             new_line = urlencode(query, doseq=True)
#             updated_lines.append(new_line)
#         else:
#             updated_lines.append(line)
#
#     # Шаг 3: возвращаем строки с fbrand/fsupplier, если они не были использованы
#     for prod, indexes in removable_lines_by_prod.items():
#         if prod not in used_prod_ids:
#             for i in indexes:
#                 updated_lines.append(lines[i])
#
#
#     return expand_fdlvr_blocks(updated_lines)
#
#
# def parse_lines(lines):
#     return [parse_qs(line) for line in lines]
#
# def build_key(query):
#     return (query.get('prod', [None])[0], query.get('xsubject', [None])[0])
#
# def expand_fdlvr_blocks(raw_lines):
#     parsed_lines = parse_lines(raw_lines)
#
#     # Группируем строки по содержимому
#     fdlvr_blocks = defaultdict(list)
#     price_blocks = defaultdict(list)
#     brand_blocks = defaultdict(list)
#     filter_blocks = defaultdict(list)
#
#     for query in parsed_lines:
#         key = build_key(query)
#         if 'fdlvr' in query:
#             fdlvr_blocks[key].append(query)
#         elif 'priceU' in query:
#             price_blocks[key].append(query)
#         elif any(k in query for k in ['fbrand', 'fsupplier']) and set(query.keys()).issubset({'prod', 'xsubject', 'fbrand', 'fsupplier'}):
#             brand_blocks[key].append(query)
#         else:
#             filter_blocks[key].append(query)
#
#     result = []
#
#     # Для каждой fdlvr строки ищем и объединяем всё остальное по ключу
#     for key, fdlvr_list in fdlvr_blocks.items():
#         prod, xsubject = key
#         filter_list = filter_blocks.get(key, [])
#         price_list = price_blocks.get(key, [])
#         brand_list = brand_blocks.get(key, [])
#
#         # если нет фильтров, то используем пустой словарь
#         if not filter_list:
#             filter_list = [{}]
#
#         for fdlvr in fdlvr_list:
#             for filters in filter_list:
#                 # объединяем fdlvr и фильтры
#                 base = {**fdlvr}
#                 for k, v in filters.items():
#                     if k not in base:
#                         base[k] = v
#
#                 # добавляем все подходящие priceU (или ни одного, если нет)
#                 prices = price_list or [{}]
#                 for price in prices:
#                     with_price = {**base}
#                     for k, v in price.items():
#                         if k not in with_price:
#                             with_price[k] = v
#
#                     # добавляем fbrand/fsupplier (если есть подходящие)
#                     brands = brand_list or [{}]
#                     for brand in brands:
#                         full = {**with_price}
#                         for k, v in brand.items():
#                             if k not in full:
#                                 full[k] = v
#                         result.append(urlencode(full, doseq=True))
#
#     return result

def transform_input(arr):
    result = []

    # Шаг 1: Очистка и замены
    cleaned = []
    replacements = {
        "fdlvr=2-4 часа": "fdlvr=4",
        "fdlvr=Сегодня": "fdlvr=12",
        "fdlvr=Завтра": "fdlvr=24",
        "fdlvr=Послезавтра": "fdlvr=48",
        "fdlvr=До 3 дней": "fdlvr=72",
        "fdlvr=До 5 дней": "fdlvr=120"
    }

    for s in arr:
        s = s.replace("param=", "").replace("&value", "")
        if "fdlvr=Любой" in s:
            continue
        for old, new in replacements.items():
            s = s.replace(old, new)
        cleaned.append(s)

    # Шаг 2: Добавление =1 к булевым параметрам
    bool_params = {
        "faction", "fnds", "frating", "foriginal",
        "fpremium", "ffeedbackpoints", "fpremiumuser"
    }

    temp_map = defaultdict(lambda: defaultdict(list))
    flat_map = defaultdict(lambda: defaultdict(list))

    for s in cleaned:
        parts = s.split("&")
        param_map = {}
        for p in parts:
            key, val = p.split("=")
            param_map[key] = val

        prod = param_map.get("prod")
        xsubject = param_map.get("xsubject")

        keys = sorted(param_map.keys())

        param_name = None
        param_value = None

        for k in keys:
            if k not in ("prod", "xsubject", "priceU"):
                param_name = k
                param_value = param_map[k]
                break

        # Обработка priceU — сохраняем как есть
        if "priceU" in param_map:
            flat_map[(prod, xsubject)]["priceU"].append(param_map["priceU"])
            continue

        # fdlvr — особый случай, каждый отдельно
        if param_name == "fdlvr":
            result.append(
                f"prod={prod}" +
                (f"&xsubject={xsubject}" if xsubject else "") +
                f"&fdlvr={param_value}"
            )
            continue

        if param_name == "priceU":
            result.append(
                f"prod={prod}" +
                (f"&xsubject={xsubject}" if xsubject else "") +
                f"&priceU={param_value}"
            )
            continue

        # Добавить =1 к булевым
        if param_name in bool_params:
            result.append(
                f"prod={prod}" +
                (f"&xsubject={xsubject}" if xsubject else "") +
                f"&{param_name}=1"
            )
            continue

        # Сбор для объединения (по prod + xsubject или prod)
        if xsubject:
            temp_map[(prod, xsubject)][param_name].append(param_value)
        else:
            flat_map[(prod, None)][param_name].append(param_value)

    # Шаг 3: Объединение значений
    for (prod, xsubject), param_dict in temp_map.items():
        for param, values in param_dict.items():
            if param is not None:
                joined_vals = "%3B".join(values)
                line = f"prod={prod}" + (f"&xsubject={xsubject}" if xsubject else "") + (f"&{param}={joined_vals}" if joined_vals else "")
                # print(line)
                # line = f"prod={prod}&xsubject={xsubject}&{param}={joined_vals}"
                result.append(line)
            else:
                if (xsubject is not None):
                    result.append(f"prod={prod}&xsubject={xsubject}")
                else:
                    result.append(f"prod={prod}")

    for (prod, xsubject), param_dict in flat_map.items():
        for param, values in param_dict.items():
            # print(f'prod = {prod}\nxsubject = {xsubject}\nparam = {param}\nvalues = {values}\n\n')
            if param is not None:
                joined_vals = "%3B".join(values)
                line = f"prod={prod}" + (f"&xsubject={xsubject}" if xsubject else "") + (f"&{param}={joined_vals}" if joined_vals else "")
                # print(line)
                result.append(line)
            else:
                if (xsubject is not None):
                    result.append(f"prod={prod}&xsubject={xsubject}")
                else:
                    result.append(f"prod={prod}")

    # print(f'transform_input\n{result}')

    return result

def group_query_params(dat):
    data = transform_input(dat)
    grouped = defaultdict(list)
    brand_supplier_map = defaultdict(list)
    brand_supplier_lines = defaultdict(dict)
    untouched_lines = []

    for line in data:
        query = parse_qs(line)
        prod = query.get('prod', [None])[0]
        xsubject = query.get('xsubject', [None])[0]
        key = (prod, xsubject)

        # fdlvr и priceU — сохраняем как есть
        if "fdlvr=" in line or "priceU=" in line:
            untouched_lines.append(line)
            continue

        # fbrand/fsupplier — сохраняем отдельно
        if "fbrand=" in line or "fsupplier=" in line:
            if "fbrand=" in line:
                brand_supplier_lines[key]["fbrand"] = '&'.join(
                    p for p in line.split('&') if p.startswith('fbrand='))
            if "fsupplier=" in line:
                brand_supplier_lines[key]["fsupplier"] = '&'.join(
                    p for p in line.split('&') if p.startswith('fsupplier='))
            continue

        # Прочие строки — группируем
        param_part = '&'.join(
            p for p in line.split('&')
            if not p.startswith('prod=') and not p.startswith('xsubject=')
        )
        grouped[key].append(param_part)

    # Формируем результат
    result = []

    # 1. Добавляем fbrand и fsupplier для каждой группы
    for (prod, xsubject), params in brand_supplier_lines.items():
        combined = [f'prod={prod}']
        if xsubject:
            combined.append(f'xsubject={xsubject}')
        if 'fbrand' in params:
            combined.append(params['fbrand'])
        if 'fsupplier' in params:
            combined.append(params['fsupplier'])
        result.append('&'.join(combined))

        # Сохраняем для добавления к другим строкам
        brand_supplier_map[(prod, xsubject)] = []
        if 'fbrand' in params:
            brand_supplier_map[(prod, xsubject)].append(params['fbrand'])
        if 'fsupplier' in params:
            brand_supplier_map[(prod, xsubject)].append(params['fsupplier'])

    # 2. Добавляем объединённые строки по другим параметрам
    for (prod, xsubject), params in grouped.items():
        prefix = f'prod={prod}'
        if xsubject:
            prefix += f'&xsubject={xsubject}'
        extra = brand_supplier_map.get((prod, xsubject), [])
        combined = '&'.join(params + extra)
        result.append(f'{prefix}&{combined}' if combined else prefix)

    # 3. Добавляем нетронутые строки (fdlvr и priceU)
    result.extend(untouched_lines)

    # print(f'group_query_params\n{result}')

    return expand_brand_supplier(result)

def expand_brand_supplier(lines):
    brand_supplier_by_prod = defaultdict(list)
    removable_lines_by_prod = defaultdict(set)

    # Шаг 1: собираем fbrand/fsupplier по prod
    for i, line in enumerate(lines):
        query = parse_qs(line)
        prod = query.get('prod', [None])[0]
        has_brand = 'fbrand' in query
        has_supplier = 'fsupplier' in query
        only_brand_or_supplier = all(k in {'prod', 'xsubject', 'fbrand', 'fsupplier'} for k in query)

        if prod and (has_brand or has_supplier):
            parts = []
            if has_brand:
                for val in query['fbrand']:
                    parts.append(('fbrand', val))
            if has_supplier:
                for val in query['fsupplier']:
                    parts.append(('fsupplier', val))
            brand_supplier_by_prod[prod].extend(parts)

            if only_brand_or_supplier:
                removable_lines_by_prod[prod].add(i)

    used_prod_ids = set()
    updated_lines = []

    # Шаг 2: добавляем fbrand/fsupplier в строки без fdlvr/priceU
    for i, line in enumerate(lines):
        if i in [i for ids in removable_lines_by_prod.values() for i in ids]:
            continue  # временно пропускаем, обработаем позже

        if 'fdlvr=' in line or 'priceU=' in line:
            updated_lines.append(line)
            continue

        query = parse_qs(line)
        prod = query.get('prod', [None])[0]

        if prod and prod in brand_supplier_by_prod:
            existing_keys = set(query.keys())
            additions_made = False
            for k, v in brand_supplier_by_prod[prod]:
                if k not in existing_keys:
                    query[k] = [v]
                    additions_made = True
            if additions_made:
                used_prod_ids.add(prod)
            new_line = unquote(urlencode(query, doseq=True))
            new_line = new_line.replace(';', '%3B')
            updated_lines.append(new_line)
        else:
            line = line.replace(';', '%3B')
            updated_lines.append(line)

    # Шаг 3: возвращаем строки с fbrand/fsupplier, если они не были использованы
    for prod, indexes in removable_lines_by_prod.items():
        if prod not in used_prod_ids:
            for i in indexes:
                updated_lines.append(lines[i])

    # print(f'expand_brand_supplier\n{updated_lines}')

    res = expand_fdlvr_blocks(updated_lines)

    # print(f'expand_fdlvr_blocks\n{res}')
    return res

def parse_lines(lines):
    return [parse_qs(line) for line in lines]

def build_key(query):
    return (query.get('prod', [None])[0], query.get('xsubject', [None])[0])

def expand_fdlvr_blocks(raw_lines):
    parsed_lines = parse_lines(raw_lines)

    # Словари с (ключ -> [(query_dict, исходная строка)])
    fdlvr_blocks = defaultdict(list)
    price_blocks = defaultdict(list)
    brand_blocks = defaultdict(list)
    filter_blocks = defaultdict(list)

    for query, raw in zip(parsed_lines, raw_lines):
        key = build_key(query)
        keys = set(query.keys())

        if 'fdlvr' in query:
            fdlvr_blocks[key].append((query, raw))
        elif 'priceU' in query:
            price_blocks[key].append((query, raw))
        elif {'fbrand', 'fsupplier'} & keys and keys.issubset({'prod', 'xsubject', 'fbrand', 'fsupplier'}):
            brand_blocks[key].append((query, raw))
        else:
            filter_blocks[key].append((query, raw))

    new_lines = []
    used_donor_lines = set()

    for key in fdlvr_blocks:
        fdlvr_list = fdlvr_blocks[key]
        filters_list = filter_blocks.get(key, [({}, '')])
        price_list = price_blocks.get(key, [({}, '')])
        brand_list = brand_blocks.get(key, [({}, '')])

        for fdlvr, fdlvr_raw in fdlvr_list:
            used_donor_lines.add(fdlvr_raw)
            for filters, filters_raw in filters_list:
                used_donor_lines.add(filters_raw)
                base = {**fdlvr, **filters}
                for price, price_raw in price_list:
                    used_donor_lines.add(price_raw)
                    with_price = {**base, **price}
                    for brand, brand_raw in brand_list:
                        used_donor_lines.add(brand_raw)
                        full = {**with_price, **brand}
                        stro = unquote(urlencode(full, doseq=True)).replace(';', '%3B')
                        new_lines.append(stro)

    # Добавляем только те строки, которые не были использованы как доноры
    untouched_lines = [line for line in raw_lines if line not in used_donor_lines]

    return new_lines + untouched_lines























@app.post("/parametres")
async def get_parametres(payload: ParametresPayload):
    global selected_ids_storage

    # print("✅ Активные ключи:", payload.activeKeys)
    # print()
    # print("💰 Цены:", payload.prices)
    # print()
    # # selected_ids_storage.append(1)
    # print (selected_ids_storage)

    # allData = []
    # for key in payload.activeKeys:
    #     allData.append(str(key))

    # for price_key, price_val in payload.prices.items():
    #     new_price_str = f"{price_key}{price_val.min*100}%3B{price_val.max*100}"
    #     allData.append(new_price_str)
    #
    # for key in selected_ids_storage:
    #     flag = True
    #     for item in allData:
    #         if f'prod={key}' in item:
    #             flag = False
    #             break
    #     if flag:
    #         allData.append(f'prod={key}')

    allData = [
        'prod=9835&xsubname=FM-трансмиттер&xsubject=764',
        'prod=9835&xsubject=764&faction=1',
        'prod=9835&xsubject=764&fnds=1',
        'prod=9835&xsubject=764&frating=1',
        'prod=9835&xsubject=764&foriginal=1',
        'prod=9835&xsubject=764&fpremium=1',
        'prod=9835&xsubject=764&ffeedbackpoints=1',
        'prod=9835&xsubject=764&fpremiumuser=1',
        'prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889',
        'prod=9835&xsubject=1889&faction=1',
        'prod=9835&xsubject=1889&fnds=1',
        'prod=9835&xsubject=1889&param=fdlvr&value=Завтра',
        'prod=9835&xsubject=1889&param=fdlvr&value=Послезавтра',
        'prod=9835&xsubject=1889&frating=1',
        'prod=9835&xsubject=1889&foriginal=1',
        'prod=9835&xsubject=1889&fpremium=1',
        'prod=9835&xsubject=1889&ffeedbackpoints=1',
        'prod=9835&xsubject=1889&fpremiumuser=1',
        'prod=9835&fbrand=194905231',
        'prod=9835&xsubject=1889&param=f11461&value=22528',
        'prod=9835&xsubject=1889&param=f14081&value=63147',
        'prod=9835&xsubject=1889&param=f15002656&value=-29856',
        'prod=9835&xsubject=1889&param=f15002656&value=-29857',
        'prod=9835&xsubject=1889&param=f746&value=10326',
        'prod=9835&xsubject=1889&param=f746&value=3658649',
        'prod=9835&xsubject=1889&param=f746&value=3698306',
        'prod=9835&xsubject=1889&param=f355315&value=371772',
        'prod=9835&xsubject=1889&param=f5023&value=109520',
        'prod=9835&xsubject=1889&priceU=50000%3B100000',
        'prod=15692'
    ]


    a=[
        'prod=9835&xsubject=1889&fdlvr=24&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&xsubname=Автомобильное+зарядное+устройство&'
        'f11461=22528&f14081=63147&f15002656=-29856%3B-29857&f746=10326%3B3658649%3B3698306&f355315=371772&f5023=109520&fbrand=194905231&priceU=50000%3B100000',

        'prod=9835&xsubject=1889&fdlvr=48&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&xsubname=Автомобильное+зарядное+устройство&'
        'f11461=22528&f14081=63147&f15002656=-29856%3B-29857&f746=10326%3B3658649%3B3698306&f355315=371772&f5023=109520&fbrand=194905231&priceU=50000%3B100000',

        'prod=9835&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&xsubname=FM-трансмиттер&fbrand=194905231',

        'prod=15692'
    ]

    # allData = [
    #     'prod=9835&xsubject=764&param=faction',
    #     'prod=9835&xsubject=764&param=fnds',
    #     'prod=9835&xsubject=764&param=frating',
    #     'prod=9835&xsubject=764&param=foriginal',
    #     'prod=9835&xsubject=764&param=fpremium',
    #     'prod=9835&xsubject=764&param=ffeedbackpoints',
    #     'prod=9835&xsubject=764&param=fpremiumuser',
    #     'prod=9835&xsubject=764&param=fdlvr&value=2-4 часа',
    #     'prod=9835&xsubject=764&param=fdlvr&value=завтра',
    #     'prod=9835&xsubject=1889&param=faction',
    #     'prod=9835&xsubject=1889&param=fnds',
    #     'prod=9835&xsubject=1889&param=fdlvr&value=завтра',
    #     'prod=9835&xsubject=1889&param=fdlvr&value=до 5 дней',
    #     'prod=9835&xsubject=1889&param=frating',
    #     'prod=9835&xsubject=1889&param=foriginal',
    #     'prod=9835&xsubject=1889&param=fpremium',
    #     'prod=9835&xsubject=1889&param=ffeedbackpoints',
    #     'prod=9835&xsubject=1889&param=fpremiumuser',
    #     'prod=9835&xsubject=1889&param=f11461&value=22528',
    #     'prod=9835&xsubject=1889&param=f11461&value=22533',
    #     'prod=9835&xsubject=1889&param=f14081&value=643600725',
    #     'prod=9835&xsubject=1889&param=f14081&value=102252956',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29856',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29855',
    #     'prod=9835&xsubject=1889&param=f746&value=9564676',
    #     'prod=9835&xsubject=1889&param=f746&value=10326',
    #     'prod=9835&xsubject=1889&param=f355315&value=371772',
    #     'prod=9835&xsubject=1889&param=f355315&value=371771',
    #     'prod=9835&xsubject=1889&param=f5023&value=214366',
    #     'prod=9835&xsubject=1889&param=f5023&value=85146',
    #     'prod=9835&param=fbrand&value=194905231',
    #     'prod=9835&param=fbrand&value=311378557',
    #     'prod=9835&param=fsupplier&value=3942301',
    #     'prod=9835&param=fsupplier&value=206677',
    #     'prod=9835&xsubject=764&priceU=100%3B200',
    #     'prod=9835&xsubject=1889&priceU=500%3B600'
    # ]

    # allData = [
    #     'prod=9835&xsubname=FM-трансмиттер&xsubject=764',
    #     'prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889',
    #     'prod=9835&xsubject=1889&faction=1',
    #     'prod=9835&xsubject=1889&fnds=1',
    #     'prod=9835&xsubject=1889&param=fdlvr&value=Завтра',
    #     'prod=9835&xsubject=1889&frating=1',
    #     'prod=9835&xsubject=1889&foriginal=1',
    #     'prod=9835&xsubject=1889&fpremium=1',
    #     'prod=9835&xsubject=1889&ffeedbackpoints=1',
    #     'prod=9835&xsubject=1889&fpremiumuser=1',
    #     'prod=9835&xsubject=1889&param=f11461&value=22528',
    #     'prod=9835&xsubject=1889&param=f14081&value=63147',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29856',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29857',
    #     'prod=9835&xsubject=1889&param=f746&value=10326',
    #     'prod=9835&xsubject=1889&param=f746&value=3658649',
    #     'prod=9835&xsubject=1889&param=f746&value=3698306',
    #     'prod=9835&xsubject=1889&param=f355315&value=371772',
    #     'prod=9835&xsubject=1889&param=f5023&value=109520',
    #     'prod=9835&xsubject=1889&priceU=50000%3B100000',
    #     'prod=15692']

    requestData = group_query_params(allData)
    print(f'requestData:\n{requestData}')
    # start_parse(requestData, 1)

    # print(f'\n\n\n1){allData}')


    # allData = [
    #     'prod=9835&xsubject=764&param=faction',
    #     'prod=9835&xsubject=764&param=fnds',
    #     'prod=9835&xsubject=764&param=frating',
    #     'prod=9835&xsubject=764&param=foriginal',
    #     'prod=9835&xsubject=764&param=fpremium',
    #     'prod=9835&xsubject=764&param=ffeedbackpoints',
    #     'prod=9835&xsubject=764&param=fpremiumuser',
    #     'prod=9835&xsubject=764&param=fdlvr&value=2-4 часа',
    #     'prod=9835&xsubject=764&param=fdlvr&value=завтра',
    #     'prod=9835&xsubject=1889&param=faction',
    #     'prod=9835&xsubject=1889&param=fnds',
    #     'prod=9835&xsubject=1889&param=fdlvr&value=завтра',
    #     'prod=9835&xsubject=1889&param=fdlvr&value=до 5 дней',
    #     'prod=9835&xsubject=1889&param=frating',
    #     'prod=9835&xsubject=1889&param=foriginal',
    #     'prod=9835&xsubject=1889&param=fpremium',
    #     'prod=9835&xsubject=1889&param=ffeedbackpoints',
    #     'prod=9835&xsubject=1889&param=fpremiumuser',
    #     'prod=9835&xsubject=1889&param=f11461&value=22528',
    #     'prod=9835&xsubject=1889&param=f11461&value=22533',
    #     'prod=9835&xsubject=1889&param=f14081&value=643600725',
    #     'prod=9835&xsubject=1889&param=f14081&value=102252956',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29856',
    #     'prod=9835&xsubject=1889&param=f15002656&value=-29855',
    #     'prod=9835&xsubject=1889&param=f746&value=9564676',
    #     'prod=9835&xsubject=1889&param=f746&value=10326',
    #     'prod=9835&xsubject=1889&param=f355315&value=371772',
    #     'prod=9835&xsubject=1889&param=f355315&value=371771',
    #     'prod=9835&xsubject=1889&param=f5023&value=214366',
    #     'prod=9835&xsubject=1889&param=f5023&value=85146',
    #     'prod=9835&param=fbrand&value=194905231',
    #     'prod=9835&param=fbrand&value=311378557',
    #     'prod=9835&param=fsupplier&value=3942301',
    #     'prod=9835&param=fsupplier&value=206677',
    #     'prod=9835&xsubject=764&priceU=100%3B200',
    #     'prod=9835&xsubject=1889&priceU=500%3B600'
    # ]

    # for key in payload.activeKeys:
    #     if "_categor_" in key:
    #         continue
    #     allData.append(str(key))
    #
    # for price_key, price_val in payload.prices.items():
    #     new_price_str = f"{price_key}{price_val.min * 100}%3B{price_val.max * 100}"
    #     allData.append(new_price_str)
    #
    # print(f'\n\n\n1){allData}\n\n')
    #
    # processed_data = []
    # for item in allData:
    #
    #     item = item.replace("param=", "").replace("&value", "")
    #
    #     special_endings = ["faction", "fnds", "frating", "foriginal", "fpremium", "ffeedbackpoin", "fpremiumuser"]
    #     for suffix in special_endings:
    #         if item.endswith(suffix):  # Если строка заканчивается на один из указанных суффиксов
    #             item += "=1"
    #
    #     delivery_replacements = {
    #         "fdlvr=2-4 часа": "fdlvr=4",
    #         "fdlvr=сегодня": "fdlvr=12",
    #         "fdlvr=завтра": "fdlvr=24",
    #         "fdlvr=послезавтра": "fdlvr=48",
    #         "fdlvr=до 3 дней": "fdlvr=72",
    #         "fdlvr=до 5 дней": "fdlvr=120"
    #     }
    #
    #     for old_value, new_value in delivery_replacements.items():
    #         if old_value in item:
    #             item = item.replace(old_value, new_value)
    #
    #     processed_data.append(item)
    #
    # allData = processed_data
    #
    # print(f'\n\n\n2){allData}\n\n')
    #
    # grouped = defaultdict(lambda: defaultdict(list))
    #
    # for query in allData:
    #     parts = query.split('&')
    #     base = parts[0]  # prod=9835
    #     subject = None
    #     for part in parts[1:]:
    #         if part.startswith('xsubject='):
    #             subject = part
    #         elif '=' in part:
    #             key, value = part.split('=')
    #             grouped[(base, subject)][key].append(value)
    #         else:
    #             grouped[(base, subject)][part] = []  # флаг без значения
    #
    # # Сборка результирующих строк
    # result = []
    # for (base, subject), params in grouped.items():
    #     query_parts = [base]
    #     if subject:
    #         query_parts.append(subject)
    #     for key, values in params.items():
    #         if values == []:
    #             query_parts.append(key)
    #         else:
    #             joined_val = ';'.join(values)
    #             # Кодируем только значения
    #             query_parts.append(f"{key}={quote(joined_val)}")
    #     result.append('&'.join(query_parts))
    #
    # # Вывод
    # for r in result:
    #     print(r)
    #
    # parsed = [dict(parse_qsl(p)) for p in result]
    #
    # # Шаг 1: Найти доп. параметры для каждого prod
    # additions_by_prod = {}
    # for d in parsed:
    #     keys = set(d.keys())
    #     if keys.issubset({'prod', 'fbrand', 'fsupplier'}):
    #         prod_val = d['prod']
    #         if prod_val not in additions_by_prod:
    #             additions_by_prod[prod_val] = {}
    #         additions_by_prod[prod_val].update({k: v for k, v in d.items() if k != 'prod'})
    #
    # # Шаг 2: Применить их ко всем остальным строкам с тем же prod
    # updated = []
    # for d in parsed:
    #     keys = set(d.keys())
    #     prod_val = d.get('prod')
    #     if keys.issubset({'prod', 'fbrand', 'fsupplier'}):
    #         continue  # пропустить строки-доноры
    #     if prod_val in additions_by_prod:
    #         d.update(additions_by_prod[prod_val])
    #     updated.append(urlencode(d, doseq=True))
    #
    # print('PREDFINAL \n\n')
    # for r in updated:
    #     print(r)
    # print('\n\n')
    #
    # b=[]
    #
    # allData = updated
    # for r in selected_ids_storage:
    #     print(f'---prod={r}')
    #     for p in updated:
    #         print(f'++++++ {str(p)}')
    #         print(f'prod={r}' in str(p))
    #         print('\n')
    #
    #         if (f'prod={r}' in str(p)) == False:
    #             b.append(r)
    #             # allData.append(f'prod={r}')
    #             break
    #
    # print(f"НЕ ВОШЛО: {b}")
    # b[:] = list(dict.fromkeys(b))
    #
    # for r in b:
    #     allData.append(f'prod={r}')
    #
    # print('FINAL \n\n')
    # for r in allData:
    #     print(r)
    #
    # # processed_data = []
    # # for item in allData:
    # #     # Шаг 1: Удаляем "param=" и "&value"
    # #     item = item.replace("param=", "").replace("&value", "")
    # #
    # #     special_endings = ["faction", "fnds", "frating", "foriginal", "fpremium", "ffeedbackpoints", "fpremiumuser"]
    # #     for suffix in special_endings:
    # #         if item.endswith(suffix):  # Если строка заканчивается на один из указанных суффиксов
    # #             item += "=1"
    # #
    # #     delivery_replacements = {
    # #         "fdlvr=2-4 часа": "fdlvr=4",
    # #         "fdlvr=сегодня": "fdlvr=12",
    # #         "fdlvr=завтра": "fdlvr=24",
    # #         "fdlvr=послезавтра": "fdlvr=48",
    # #         "fdlvr=до 3 дней": "fdlvr=72",
    # #         "fdlvr=до 5 дней": "fdlvr=120"
    # #     }
    # #
    # #     for old_value, new_value in delivery_replacements.items():
    # #         if old_value in item:
    # #             item = item.replace(old_value, new_value)
    # #
    # #     processed_data.append(item)
    # #
    # # allData = processed_data
    # #
    # # # print(f'\n\n\n2){allData}')
    # #
    # #
    # #
    # # grouped = defaultdict(lambda: defaultdict(list))
    # #
    # # for query in allData:
    # #     parts = query.split('&')
    # #     base = parts[0]  # prod=9835
    # #     subject = None
    # #     for part in parts[1:]:
    # #         if part.startswith('xsubject='):
    # #             subject = part
    # #         elif '=' in part:
    # #             key, value = part.split('=')
    # #             grouped[(base, subject)][key].append(value)
    # #         else:
    # #             grouped[(base, subject)][part] = []  # флаг без значения
    # #
    # # # Сборка результирующих строк
    # # result = []
    # # for (base, subject), params in grouped.items():
    # #     query_parts = [base]
    # #     if subject:
    # #         query_parts.append(subject)
    # #     for key, values in params.items():
    # #         if values == []:
    # #             query_parts.append(key)
    # #         else:
    # #             joined_val = ';'.join(values)
    # #             # Кодируем только значения
    # #             query_parts.append(f"{key}={quote(joined_val)}")
    # #     result.append('&'.join(query_parts))
    # #
    # #
    # # print('\n\n\n3)')
    # # for url in result:
    # #     print(url)
    # #
    # # parsed = [dict(parse_qsl(p)) for p in result]
    # #
    # # additions_by_prod = {}
    # # filtered = []
    # #
    # # for d in parsed:
    # #     keys = set(d.keys())
    # #     prod_val = d.get('prod')
    # #     if keys.issubset({'prod', 'fbrand', 'fsupplier'}):
    # #         if prod_val not in additions_by_prod:
    # #             additions_by_prod[prod_val] = {}
    # #         additions_by_prod[prod_val].update({k: v for k, v in d.items() if k != 'prod'})
    # #     else:
    # #         filtered.append(d)
    # #
    # # # print(filtered)
    # # # print(result)
    # # # print()
    # #
    # #
    # #
    # # # --- 2. Применяем значения из доноров к остальным строкам с тем же prod ---
    # # updated = []
    # # used_prods = set()
    # #
    # # for d in filtered:
    # #     prod_val = d.get('prod')
    # #     if prod_val not in additions_by_prod:
    # #         d.update(additions_by_prod[prod_val])
    # #     updated.append(d)
    # #     if prod_val:
    # #         used_prods.add(str(prod_val))
    # #
    # # print("-----")
    # # print(used_prods)
    # #
    # # # --- 3. Добавляем строки prod=номер в allData, если они отсутствуют ---
    # # for prod in selected_ids_storage:
    # #     if str(prod) not in used_prods:
    # #         result.append(f'prod={prod}')
    # #
    # #     # for item in allData:
    # #     #     if f'prod={prod}' in item:
    # #     #         continue
    # #     # else:
    # #     #     result.append(f'prod={prod}')
    # #
    # # # # --- 4. Перекодируем обновленные строки в формат URL ---
    # # # final = [urlencode(d, doseq=True) for d in updated]
    # # #
    # # # # --- 5. Добавляем prod=номер строки из предыдущего шага ---
    # # # for prod in selected_ids_storage:
    # # #     if str(prod) not in used_prods:
    # # #         final.append(f'prod={prod}')
    # # #
    # # # # allData = final
    # #
    # # print(f'-----\n\n\n5) Финальный результат:')
    # # # for url in final:
    # # for url in result:
    # #     print(url)
    # #
    # # # --- 4. Перекодируем обновленные строки в формат URL ---
    # # # final = [urlencode(d, doseq=True) for d in updated]
    # # #
    # # # # --- 5. Добавляем prod=номер строки из предыдущего шага ---
    # # # for prod in selected_ids_storage:
    # # #     if str(prod) not in used_prods:
    # # #         final.append(f'prod={prod}')
    # #
    # #
    # # # # Шаг 3: Модификация allData
    # # # resultData = []
    # # # for item in allData:
    # # #     item_str = str(item)
    # # #
    # # #     # Шаг 3.1: Исключение ненужных значений
    # # #     if "_fdlvr_любой" in item_str:
    # # #         continue
    # # #
    # # #     # Шаг 3.2: Преобразование значений доставки
    # # #     if "_fdlvr_" in item_str:
    # # #         item_str = item_str.replace("_fdlvr_2-4 часа", "_fdlvr_4") \
    # # #                            .replace("_fdlvr_сегодня", "_fdlvr_12") \
    # # #                            .replace("_fdlvr_завтра", "_fdlvr_24") \
    # # #                            .replace("_fdlvr_послезавтра", "_fdlvr_48") \
    # # #                            .replace("_fdlvr_до 3 дней", "_fdlvr_72") \
    # # #                            .replace("_fdlvr_до 5 дней", "_fdlvr_120")
    # # #
    # # #     # Шаг 3.3: Преобразование параметров
    # # #     if any(param in item_str for param in [
    # # #         "_param_faction",
    # # #         "_param_fnds",
    # # #         "_param_frating",
    # # #         "_param_foriginal",
    # # #         "_param_fpremium",
    # # #         "_param_ffeedbackpoints",
    # # #         "_param_fpremiumuser"
    # # #     ]):
    # # #         if not item_str.endswith("_1"):
    # # #             item_str += "_1"
    # # #
    # # #     resultData.append(item_str)
    # # #
    # # # print(f'\n\n\n2){resultData}\n\n')
    # # #
    # # # # Шаг 4: Удаление дубликатов и сортировка
    # # # resultData = sorted(set(resultData))
    # # #
    # # # print(f'\n\n\n3){resultData}\n\n')
    # # #
    # # # # Шаг 5: Группировка по prod и xsubject
    # # # grouped_prod = defaultdict(lambda: defaultdict(list))
    # # #
    # # # for item in resultData:
    # # #     parts = item.split("_")
    # # #
    # # #     if parts[0] != "prod":
    # # #         continue
    # # #
    # # #     prod_id = parts[1]
    # # #     if "xsubject" in parts:
    # # #         xsubject_index = parts.index("xsubject")
    # # #         xsubject_id = parts[xsubject_index + 1]
    # # #         key = f"prod_{prod_id}_xsubject_{xsubject_id}"
    # # #         rest = parts[xsubject_index + 2:]
    # # #     else:
    # # #         key = f"prod_{prod_id}"
    # # #         rest = parts[2:]
    # # #
    # # #     # Преобразование: param_fname_value_XXX -> fname_XXX, param_fname_1 -> fname_1
    # # #     if rest and rest[0] == "param":
    # # #         rest.pop(0)
    # # #
    # # #     if len(rest) >= 3 and rest[1] == "value":
    # # #         new_key = f"{rest[0]}_{rest[2]}"
    # # #     else:
    # # #         new_key = "_".join(rest)
    # # #
    # # #     grouped_prod[prod_id][key].append(new_key)
    # # #
    # # # # Шаг 6: Добавление fbrand и fsupplier в строки с одинаковым prod, но разным xsubject
    # # # finalResult = []
    # # # for prod_id, xsubj_groups in grouped_prod.items():
    # # #     for group_key, values in xsubj_groups.items():
    # # #         # Добавляем fbrand и fsupplier
    # # #         if group_key.endswith("_xsubject"):
    # # #             finalResult.append(f"{group_key}_" + "_".join(values) + "_fbrand_194905231%3B311378557_fsupplier_4106325%3B3942301")
    # # #
    # # #         else:
    # # #             finalResult.append(f"{group_key}_" + "_".join(values))
    # # #
    # # # print(f'\n\n\n4){finalResult}\n\n')
    # # #
    # # # # Шаг 7: Замена запятых на "%3B" и форматирование строки
    # # # formatted_result = []
    # # # for item in finalResult:
    # # #     formatted_item = item.replace(",", "%3B") \
    # # #                          .replace("_", "=") \
    # # #                          .replace("param", "") \
    # # #                          .replace("priceU", "priceU=")
    # # #     formatted_result.append(formatted_item)
    # # #
    # # # print(f'\n\n\n5){finalResult}\n\n')
    # # #
    # # # # Шаг 8: Добавление строк с prod=(номер ID категории товаров)
    # # # final_output = formatted_result
    # # # for prod_id in selected_ids_storage:
    # # #     if not any(f"prod={prod_id}" in item for item in final_output):
    # # #         final_output.append(f"prod={prod_id}")
    # # #
    # # # # Вывод результата
    # # # print("📋 Обработанный список finalResult:")
    # # # for item in final_output:
    # # #     print(item)
    # # #
    # # # return {"status": "ok"}
    # return