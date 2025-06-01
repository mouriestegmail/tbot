import configparser
martin = 799070257
andrei = 124768943
bot_connect_group = -4982847677
users = [andrei, martin, bot_connect_group]

log_dir = ""
prison_dir = ""
commands_dir = ""
except_dir = ""
token = ""
config_json = ""
watch_dir = ""
cost = {}


mode_worker = ""
mode_buyer = "_buyer"
mode_dev = "_dev"
mode_mac = "_mac"

mode = mode_worker

short_to_full = {
    "kil": "Зелье Киллера",
    "pob": "Зелье Победителя",
    "med": "Зелье Медика",
    "agt": "Зелье Агента",
    "ser": "Серная кислота",
}

def read_config(arg):
    global log_dir, prison_dir, commands_dir, except_dir, token, config_json, watch_dir, mode

    if arg == "-b":
        mode = mode_buyer
    if arg == "-d":
        mode = mode_dev
    if arg == "-m":
        mode = mode_mac

    sect = "general"
    config = configparser.ConfigParser()
    fn = "./config" + mode + ".ini"
    res = config.read(fn)

    print(fn)

    if len(res) == 0:
        print(f"check {fn} file")
        exit(-1)

    sections = config.sections()

    if sect not in sections:
        print(f"no section in config file. section = {sect}")
        print(sections)
        exit(-1)

    s_log_dir = "log_dir"
    s_prison_dir = "prison_dir"
    s_commands_dir = "commands_dir"
    s_except_dir = "except_dir"
    s_token = "token"
    s_config_json = "config_json"
    s_watchdir = "watch_dir"
    s_med = "med"
    s_pob = "pob"

    print(s_log_dir)
    for i in s_log_dir, s_prison_dir, s_commands_dir, s_except_dir, s_token, s_config_json:
        if i not in config[sect]:
            print(f"check {fn} file: {i}")
            exit(-1)

    log_dir = config[sect][s_log_dir]
    prison_dir = config[sect][s_prison_dir]
    commands_dir = config[sect][s_commands_dir]
    except_dir = config[sect][s_except_dir]
    token = config[sect][s_token]
    config_json = config[sect][s_config_json]
    watch_dir = config[sect][s_watchdir]
    med_list = config[sect][s_med].split("_")
    pob_list = config[sect][s_pob].split("_")
    med = [float(med_list[0]), float(med_list[1])]
    pob = [float(pob_list[0]), float(pob_list[1])]

    cost[s_med] = med
    cost[s_pob] = pob


