# file_utils.py

import os
import config

def files_tree():
    result = []
    for root, dirs, files in os.walk(config.log_path):
        level = root.replace(config.log_path, '').count(os.sep)
        indent = ' ' * 4 * level
        result.append(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            result.append(f'{sub_indent}{f}')
    return '\n'.join(result)

def split_text_into_chunks(text, max_size=4000):
    lines = text.splitlines()
    chunks, chunk = [], []
    size = 0
    for line in lines:
        line_size = len(line) + 1
        if size + line_size > max_size:
            chunks.append('\n'.join(chunk))
            chunk, size = [], 0
        chunk.append(line)
        size += line_size
    if chunk:
        chunks.append('\n'.join(chunk))
    return chunks
