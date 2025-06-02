import subprocess
import time
import logging
# import wmi

vm_list = [
    "C:\\VMs\\vm1.vmx",
    "C:\\VMs\\vm2.vmx",
    "C:\\VMs\\vm3.vmx",
]

cooldown = 30 * 60  # 30 минут между приостановками

logging.basicConfig(
    filename='vm_manager.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_and_print(msg):
    print(msg)
    logging.info(msg)



def get_cpu_temperature():
    # w = wmi.WMI(namespace="root\\wmi")
    # temperature_info = w.MSAcpi_ThermalZoneTemperature()
    # if not temperature_info:
    #     return None  # Не удалось получить данные
    # # Обычно возвращается список, берем первую зону
    # temp_kelvin_x10 = temperature_info[0].CurrentTemperature
    # # Переводим из десятых долей Кельвина в Цельсии
    # temp_celsius = (temp_kelvin_x10 / 10) - 273.15
    # return round(temp_celsius, 1)
    return 5

def suspend_vm(vm_path):
    log_and_print(f"Suspending VM: {vm_path}")
    # subprocess.run(["vmrun", "suspend", vm_path])

def resume_vm(vm_path):
    log_and_print(f"Resuming VM: {vm_path}")
    # subprocess.run(["vmrun", "start", vm_path])

def get_running_vms():
    result = subprocess.run(["vmrun", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()

    print(f"run VM:")
    print(lines)

    if len(lines) > 1:
        return lines[1:]


last_suspend_time = 0
morning_flag = False

while True:
    now = time.localtime()
    temp = get_cpu_temperature()
    log_and_print(f"Current CPU temperature: {temp}°C")
    if True:
        if 7 <= now.tm_hour < 22 and False:
            if not morning_flag:
                log_and_print("Morning started: resuming suspended or stopped VMs")
                running = get_running_vms()
                for vm in vm_list:
                    if vm not in running:
                        resume_vm(vm)
                morning_flag = True
        else:
            morning_flag = False

        if not morning_flag:
            if temp > 0 and (time.time() - last_suspend_time) > cooldown:
                running = get_running_vms()
                # Выбираем запущенную ВМ для приостановки
                running_vms_to_suspend = [vm for vm in vm_list if vm in running]
                if running_vms_to_suspend:
                    vm_to_suspend = running_vms_to_suspend[0]
                    suspend_vm(vm_to_suspend)
                    last_suspend_time = time.time()
                else:
                    log_and_print("Нет запущенных ВМ для приостановки")
            else:
                log_and_print(f"Температура OK ({temp}°C) или ждем кулдаун, без действий")

    time.sleep(60)
