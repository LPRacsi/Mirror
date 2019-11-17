import subprocess
import time

while True:
    print('Turn off monitor')
    subprocess.run('fbset -accel false', shell=True)
    subprocess.run('tvservice -o', shell=True)
    time.sleep(5)
    print(subprocess.check_output('tvservice -s', shell=True))
    console = subprocess.check_output('tvservice -s', shell=True).split()[1]
    print('Console', console)
    if console == b'0x120002':
        print('sima Siker')
    print('Turn on monitor')
    subprocess.run('tvservice -p', shell=True)
    subprocess.run('fbset -accel true', shell=True)
    print(subprocess.check_output('tvservice -s', shell=True))
    time.sleep(10)
