import re
import ast
from tabulate import tabulate

def parse_to_table(data: str) -> str:
    # Парсинг данных
    sold_data = []
    ah_data = []
    storage_data = []

    # Разделение данных по секциям
    sections = re.split(r'\nsold:|\nAH:|\nstorage:', data)

    # Парсинг секции sold
    sold_lines = sections[1].strip().split('\n')
    for line in sold_lines:
        sold_data.append(ast.literal_eval(line.strip()))

    # Парсинг секции AH
    ah_lines = sections[2].strip().split('\n')
    for line in ah_lines:
        ah_data.append(ast.literal_eval(line.strip()))

    # Парсинг секции storage
    storage_lines = sections[3].strip().split('\n')
    for line in storage_lines:
        if line.startswith("{") and line.endswith("}"):
            storage_data.append(ast.literal_eval(line.strip()))

    # Парсинг последней строки с числом
    final_value = re.search(r'\$(\d+)', data).group(0)

    # Добавление столбца с суммой, игнорируя 'z'
    def add_sum_column(data, ignore_columns=None):
        if ignore_columns is None:
            ignore_columns = []
        for row in data:
            sum_value = sum(value for key, value in row.items() if key not in ignore_columns)
            row['sum'] = sum_value

    # Применение функции
    add_sum_column(sold_data)
    add_sum_column(ah_data, ignore_columns=['z'])
    add_sum_column(storage_data)

    # Форматирование и возврат данных в виде строки
    def format_table(title, data):
        if not data:
            return f"{title}:"

        headers = data[0].keys()
        table = [headers] + [list(row.values()) for row in data]

        if len(data) > 1:
            total = {header: 0 for header in headers}
            for row in data:
                for key in total.keys():
                    if key != 'sum':
                        total[key] += row.get(key, 0)
            total['sum'] = sum(row['sum'] for row in data)
            table.append(["-" * len(str(total[header])) for header in headers])
            table.append(list(total.values()))

        return f"{title}:\n" + tabulate(table, headers='firstrow', tablefmt='grid')

    # Формирование таблиц
    result = []
    result.append(format_table("sold", sold_data))
    result.append(format_table("AH", ah_data))
    result.append(format_table("storage", storage_data))
    result.append(f"\n[{final_value}]")

    return "\n".join(result)


