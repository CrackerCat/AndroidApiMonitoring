import frida
import os
import logging
import sys
import time

if 'LOG_LEVEL' in os.environ:
    log_level = os.environ['LOG_LEVEL']
else:
    log_level = logging.INFO

LOCAL_URL_EMULATOR = "http://127.0.0.1:21212"
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=log_level)


file_log_frida = os.path.join(os.getcwd(), "logs")


def on_message(message, data):
    print((file_log_frida))
    file_log = open(file_log_frida, "a")
    if message['type'] == 'send':
        file_log.write(str(message["payload"])+"\n")

    elif message['type'] == 'error':
        file_log.write(str(message["stack"])+"\n")
    file_log.close()


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


def main():
    # app already installed and frida already running on device
    package_name = sys.argv[1]
    execution_time = int(sys.argv[2])
    file_api_to_monitoring = sys.argv[3]
    list_api_to_monitoring = read_api_to_monitoring(file_api_to_monitoring)

    pid = None
    device = None
    session = None
    try:
        device = frida.get_usb_device()
        pid = device.spawn([package_name])
        session = device.attach(pid)
    except Exception as e:
        logger.error("Error {}".format(e))

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
        end = time.time()
        if int(end - start) > execution_time:
            session.detach()
            break


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main()
    else:
        print("[*] Usage: python frida_monitoring.py com.example.app 5000 api.txt")