import sys
sys.path.append('./mnbot')
import mnbot.helper_items as hi
import mnbot.global_const as mn_gc
import mnbot.readconf as mn_conf
import file_utils

mn_gc.file_config = "C:/share/config.json"

config = mn_conf.Config()

def get_inventory_apples(dir_ss) -> str:
    fn_tmp = "inv.png"

    fns = file_utils.get_all_files(fn_tmp, dir_ss)

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

