from collections import defaultdict
from urllib.parse import parse_qs, urlencode, unquote
import os, json

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
                print(1)
                if (xsubject is not None):
                    result.append(f"prod={prod}&xsubject={xsubject}")
                    print(2)
                else:
                    result.append(f"prod={prod}")
                    print(3)

    for (prod, xsubject), param_dict in flat_map.items():
        for param, values in param_dict.items():
            # print(f'prod = {prod}\nxsubject = {xsubject}\nparam = {param}\nvalues = {values}\n\n')
            if param is not None:
                joined_vals = "%3B".join(values)
                line = f"prod={prod}" + (f"&xsubject={xsubject}" if xsubject else "") + (f"&{param}={joined_vals}" if joined_vals else "")
                # print(line)
                result.append(line)
            else:
                print(4)
                if (xsubject is not None):
                    result.append(f"prod={prod}&xsubject={xsubject}")
                    print(5)
                else:
                    result.append(f"prod={prod}")
                    print(6)

    print(f'transform_input\n{result}')

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

    print(f'group_query_params\n{result}')

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

    print(f'expand_brand_supplier\n{updated_lines}')

    res = expand_fdlvr_blocks(updated_lines)

    print(f'expand_fdlvr_blocks\n{res}')
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



# def expand_fdlvr_blocks(raw_lines):
#     parsed_lines = parse_lines(raw_lines)
#
#     print(f'parse_lines\n{parsed_lines}')
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
#             # print(f'fdlvr_blocks\n{query}')
#             fdlvr_blocks[key].append(query)
#         elif 'priceU' in query:
#             # print(f'priceU_blocks\n{query}')
#             price_blocks[key].append(query)
#         elif any(k in query for k in ['fbrand', 'fsupplier']) and set(query.keys()).issubset({'prod', 'xsubject', 'fbrand', 'fsupplier'}):
#             # print(f'fbrand_fsupplier_blocks\n{query}')
#             brand_blocks[key].append(query)
#         else:
#             # print(f'another\n{query}')
#             filter_blocks[key].append(query)
#
#     for filter in filter_blocks:
#         print(f'+_+_+ {filter}')
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
#                         stro = unquote(urlencode(full, doseq=True))
#                         stro = stro.replace(';', '%3B')
#                         result.append(stro)
#
#     return result


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
# output = transform_input(allData)
output = group_query_params(allData)
print('\n\n\n\n\n')
for line in output:
    print(line)



"prod=9835&xsubject=764&faction=1",
"prod=9835&xsubject=764&fnds=1",
"prod=9835&xsubject=764&frating=1",
"prod=9835&xsubject=764&foriginal=1",
"prod=9835&xsubject=764&fpremium=1",
"prod=9835&xsubject=764&ffeedbackpoints=1",
"prod=9835&xsubject=764&fpremiumuser=1",

"prod=9835&xsubject=764&fdlvr=4",
"prod=9835&xsubject=764&fdlvr=24",

"prod=9835&xsubject=1889&faction=1",
"prod=9835&xsubject=1889&fnds=1",
"prod=9835&xsubject=1889&fdlvr=24",
"prod=9835&xsubject=1889&fdlvr=120",
"prod=9835&xsubject=1889&frating=1",
"prod=9835&xsubject=1889&foriginal=1",
"prod=9835&xsubject=1889&fpremium=1",
"prod=9835&xsubject=1889&ffeedbackpoints=1",
"prod=9835&xsubject=1889&fpremiumuser=1",
"prod=9835&xsubject=1889&f11461=22528",
"prod=9835&xsubject=1889&f11461=22533",
"prod=9835&xsubject=1889&f14081=643600725",
"prod=9835&xsubject=1889&f14081=102252956",
"prod=9835&xsubject=1889&f15002656=-29856",
"prod=9835&xsubject=1889&f15002656=-29855",
"prod=9835&xsubject=1889&f746=9564676",
"prod=9835&xsubject=1889&f746=10326",
"prod=9835&xsubject=1889&f355315=371772",
"prod=9835&xsubject=1889&f355315=371771",
"prod=9835&xsubject=1889&f5023=214366",
"prod=9835&xsubject=1889&f5023=85146",
"prod=9835&fbrand=194905231",
"prod=9835&fbrand=311378557",
"prod=9835&fsupplier=3942301",
"prod=9835&fsupplier=206677",
"prod=9835&xsubject=764&priceU=100%3B200",
"prod=9835&xsubject=1889&priceU=500%3B600"

"prod=9835&xsubname=FM-трансмиттер&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&fdlvr=4&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=100%3B200",
"prod=9835&xsubname=FM-трансмиттер&xsubject=764&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&fdlvr=24&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=100%3B200"
"prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&faction=1&fnds=1&fdlvr=24&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=500%3B600",
"prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&faction=1&fnds=1&fdlvr=120&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=500%3B600",

"prod=9835&xsubname=FM-трансмиттер&xsubject=764&fdlvr=4&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=100%3B200"
"prod=9835&xsubname=FM-трансмиттер&xsubject=764&fdlvr=24&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=100%3B200"
"prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&fdlvr=24&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=500%3B600"
"prod=9835&xsubname=Автомобильное зарядное устройство&xsubject=1889&fdlvr=120&faction=1&fnds=1&frating=1&foriginal=1&fpremium=1&ffeedbackpoints=1&fpremiumuser=1&f11461=22528%3B22533&f14081=643600725%3B102252956&f15002656=-29856%3B-29855&f746=9564676%3B10326&f355315=371772%3B371771&f5023=214366%3B85146&fbrand=194905231%3B311378557&fsupplier=3942301%3B206677&priceU=500%3B600"
