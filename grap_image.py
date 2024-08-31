try:
    import sys
    import mnbot.helper_items as hi
    import mnbot.readconf as mn_conf
    import file_utils
    import os

    sys.path.append('./mnbot')
    config = mn_conf.Config()
except Exception as e:
    print(e)

def get_all_files(template: str, folder: str) -> list:
    res = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if template in file:
                res.append(os.path.join(root, file))

    return res
def get_inventory_apples(dir_ss) -> str:
    print("test")
    fn_tmp = "inv.png"
    print(dir_ss, fn_tmp)

    try:
        fns = file_utils.get_all_files(fn_tmp, dir_ss)
    except Exception as e:
        print(e)
    print(fns)

    apples = dict()
    sum = 0

    for fn in fns:
        print(fn)
        for a in config.apples:
            count = len(hi.get_points_items(start=None,
                                     size=None,
                                     delta_worker=None,
                                     item_paths=a.imgs,
                                     bigpath=fn
                                     ))
            sum += count

            apples[a.name] = apples.get(a.name, 0) + count
    print(apples)
    return f'str(apples).replace(" ","")  {sum}'

