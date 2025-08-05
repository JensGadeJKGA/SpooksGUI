import os
import datetime

def log_usage():

    import getpass
    import socket
    try:
        log_path = r"O:\Organisation\DK_1551\Diverse\SpooksLog"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = getpass.getuser()
        pc_name = socket.gethostname()
        log = os.path.join(log_path, "log.log")
        with open(log, "a") as f:
            f.write(f"{timestamp}\t{user.upper()}\t{pc_name.upper()}\n")
    except:
        pass