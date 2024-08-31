def get_all_files(template: str, folder: str) -> list:
    res = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if template in file:
                res.append(os.path.join(root, file))

    return res