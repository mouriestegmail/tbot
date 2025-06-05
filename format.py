import os
from datetime import datetime
import time

import config


def get_storage(an:int):
    l_dir = config.log_dir
    fn = l_dir + f'\\storage_an{an}.ah'

    name = "{stor:" + f"{an}, "
    err = name + "error }\n"

    try:
        if os.path.exists(fn):
            last_modified_time = os.path.getmtime(fn)
            current_time = time.time()
            delta_t = 60 * 10
            if current_time - last_modified_time <= delta_t:
                with open(fn, 'r') as file:
                    first_line = file.readline().strip()

                    apples = eval(first_line)
                    apples = dict(sorted(apples.items()))

                    for key in list(apples):
                        if apples[key] == 0:
                            del apples[key]

                    res = str(apples)

                    res = res.replace("{", name)
                    res = res.replace(": ", ":")
                    res += "\n"
                    return res
    except Exception as e:
        print(e)
    return err





'''import re
from typing import List, Dict


def parse_to_table(data: str) -> str:
    def parse_data(text: str) -> Dict[str, List[Dict[str, int]]]:
        sections = re.split(r'\n(?=[a-zA-Z]+:)', text.strip())
        data = {}
        for section in sections:
            header, *rows = section.split('\n')
            name = header.strip(':')
            rows = [eval(row.strip()) for row in rows if row.strip()]
            data[name] = rows
        return data

    def create_table(data: List[Dict[str, int]], headers: List[str], include_z: bool = False) -> str:
        # Заголовок и разделитель
        header_row = "|".join(f"{h[:1]}".center(3) for h in headers) + "|sum\n"
        separator_row =  "|".join(["-" * 3 for _ in headers]) + "|---\n"
        separator_row_full = "-" + "-".join(["-" * 3 for _ in headers]) + "-----\n"

        data_rows = ""
        totals = {header: 0 for header in headers}
        sum_total = 0

        for row in data:
            row_values = [str(row.get(h, 0)).rjust(3)[:3] for h in headers]
            row_sum = sum(int(row.get(h, 0)) for h in headers if (h != 'z'))
            sum_total += row_sum
            data_row =  "|".join(value.center(3) for value in row_values) + f"|{row_sum:>3}\n"
            data_rows += data_row
            for header in headers:
                if header != 'z' or include_z:
                    totals[header] += row.get(header, 0)

        sum_row = "|".join(f"{str(totals[header]).rjust(3)[:3]}" for header in headers) + f"|{sum_total:>3}\n"


        if len(data) > 1:
            return  header_row + separator_row + data_rows + separator_row + sum_row
        else:
            return header_row + separator_row + data_rows

    # Парсинг входных данных
    data_dict = parse_data(data)

    # Генерация таблиц
    sold_table = create_table(data_dict['sold'], ['agt', 'med', 'pob', 'ser'])
    ah_table = create_table(data_dict['AH'], ['agt', 'med', 'pob', 'ser', 'z'], include_z=True)
    storage_table = create_table(data_dict['storage'], ['agt', 'med', 'pob', 'ser'])

    # Объединение таблиц в один текстовый блок
    result = "Sold:\n" + sold_table + "\nAH:\n" + ah_table + "\nStorage:\n" + storage_table

    return result


data_text = """
sold:
{'agt': 20, 'med': 12, 'pob': 18, 'ser': 12}
{'agt': 18, 'med': 7, 'pob': 17, 'ser': 5}
{'agt': 13, 'med': 6, 'pob': 11, 'ser': 9}
{'agt': 8, 'med': 0, 'pob': 8, 'ser': 7}
{'agt': 16, 'med': 9, 'pob': 18, 'ser': 9}
{'agt': 14, 'med': 15, 'pob': 16, 'ser': 12}
AH:
{'agt': 1, 'med': 3, 'pob': 2, 'ser': 1, 'z': 5}
{'agt': 2, 'med': 2, 'pob': 3, 'ser': 1, 'z': 3}
{'agt': 1, 'med': 2, 'pob': 2, 'ser': 2, 'z': 4}
{'agt': 0, 'med': 1, 'pob': 3, 'ser': 0, 'z': 2}
{'agt': 2, 'med': 1, 'pob': 1, 'ser': 2, 'z': 6}
{'agt': 3, 'med': 3, 'pob': 1, 'ser': 1, 'z': 1}
storage:
{'agt': 1, 'med': 2, 'pob': 3, 'ser': 1}
"""

# print(parse_to_table(data_text))
'''