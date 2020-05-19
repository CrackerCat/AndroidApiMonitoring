import frida
import os
import logging
import sys
import time
from adb import ADB
from androguard.core.bytecodes.apk import APK
import json 
from datetime import datetime

if 'LOG_LEVEL' in os.environ:
    log_level = os.environ['LOG_LEVEL']
else:
    log_level = logging.INFO

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=log_level)


file_log_frida = os.path.join(os.getcwd(), "logs")


def on_message(message, data):
    file_log = open(file_log_frida, "a")
    if message['type'] == 'send':
        if "Error" not in str(message["payload"]):
            message_new = message["payload"]
            message_new["time"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            file_log.write(str(message_new) + "\n")
            print(str(message_new)+"\n")
    file_log.close()



def push_and_start_frida_server(adb: ADB):
    """
    Push and start adb server on device
    Parameters
    ----------
    adb

    Returns
    -------

    """
    frida_server = os.path.join(os.getcwd(), "resources", "frida-server", "frida-server")

    try:
        adb.execute(['root'])
    except Exception as e:
        adb.kill_server()
        logger.error("Error on adb {}".format(e))

    logger.info("Push frida server")
    try:
        adb.push_file(frida_server, "/data/local/tmp")
    except Exception as e:
        pass
    logger.info("Add execution permission to frida-server")
    chmod_frida = ["chmod 755 /data/local/tmp/frida-server"]
    adb.shell(chmod_frida)
    logger.info("Start frida server")
    start_frida = ["cd /data/local/tmp && ./frida-server &"]
    adb.shell(start_frida, is_async=True)


def read_api_to_monitoring(file_api_to_monitoring):
    if os.path.exists(file_api_to_monitoring):
        list_api_to_monitoring = []
        content = []
        with open(file_api_to_monitoring) as file_api:
            content = file_api.readlines()
        content = [x.strip() for x in content]
        for class_method in content:
            list_api_to_monitoring.append((class_method.split(",")[0], class_method.split(",")[1]))
        return list_api_to_monitoring
    else:
        return None


def create_script_frida(list_api_to_monitoring: list, path_frida_script_template: str):
    with open(path_frida_script_template) as frida_script_file:
        script_frida_template = frida_script_file.read()

    script_frida = ""
    for tuple_class_method in list_api_to_monitoring:
        script_frida += script_frida_template.replace("class_name", "\"" + tuple_class_method[0] + "\""). \
                            replace("method_name", "\"" + tuple_class_method[1] + "\"") + "\n\n"
    return script_frida


def main(app_path, file_api_to_monitoring, app_to_install=True):

    list_api_to_monitoring = read_api_to_monitoring(file_api_to_monitoring)
    
    if app_to_install: 
        app = APK(app_path)
        package_name = app.get_package()
        logger.info("Start ADB")
        adb = ADB()
        logger.info("Install APP")
        adb.install_app(app_path)
        logger.info("Frida Initialize")
        push_and_start_frida_server(adb)
    else:
        package_name = app_path
        adb = ADB()
        logger.info("Frida Initialize")
        push_and_start_frida_server(adb)

    pid = None
    device = None
    session = None
    
    try:
        device = frida.get_usb_device()
        pid = device.spawn([package_name])
        session = device.attach(pid)
    
    except Exception as e:
        logger.error("Error {}".format(e))
        device = frida.get_usb_device()
        pid = device.spawn([package_name])
        session = device.attach(pid)

    logger.info("Succesfully attacched frida to app")

    global file_log_frida

    dir_frida = os.path.join(file_log_frida, package_name.replace(".","_"))
    if not os.path.exists(dir_frida):
        os.makedirs(dir_frida)

    file_log_frida = os.path.join(dir_frida,  "monitoring_api_frida_{}.txt".format(package_name.replace(".", "_")))

    script_frida = create_script_frida(list_api_to_monitoring,
                                       os.path.join(os.getcwd(), "frida_scripts", "frida_script_template.js"))

    script = session.create_script(script_frida.strip().replace("\n", ""))
    script.on("message", on_message)
    script.load()

    device.resume(pid)
    start = time.time()
    while True:
        command = input("Press 0 to exit\n\nApi Invoked:\n")
        if command == "0":
            break
    

if __name__ == "__main__":
    if len(sys.argv) == 4:
        app_path = sys.argv[2]
        if os.path.exists(app_path):
            file_api_to_monitoring = sys.argv[3]
            main(app_path, file_api_to_monitoring, app_to_install=True)
        else:
            print("File {} not found".format(app_path))
    elif len(sys.argv) == 3:
        package_name = sys.argv[1]
        file_api_to_monitoring = sys.argv[2]
        main(package_name, file_api_to_monitoring, app_to_install=False)

    else:
        print("[*] Usage: python frida_monitoring.py -f app.apk api.txt")
        print("[*] Usage: python frida_monitoring.py package.name api.txt")