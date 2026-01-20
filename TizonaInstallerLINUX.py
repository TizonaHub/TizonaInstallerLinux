import sys
import os
import shutil
import json
import locale
import pickle
import subprocess
from zipfile import ZipFile
import json

args = sys.argv
startFile = '/opt/TizonaHub/TizonaServer/start.js'

# LANG
eng = {
    "uninstall_warning_1": "You are about to uninstall TizonaHub, press C to continue or Q to cancel",
    "uninstall_warning_2": "Are you sure? You will have to manually remove the database and the user if you wish.",
    "uninstall_warning_3": "Python, Node.js and MySQL will remain installed.",
    "uninstall_press": "Press C to continue or Q to cancel",
    "uninstall_done": "Uninstallation completed",
    "up_to_date":'TizonaHub is up to date!'
}
esp = {
    "uninstall_warning_1": "Estás a punto de desinstalar TizonaHub, pulsa C para continuar o Q para cancelar",
    "uninstall_warning_2": "¿Estás seguro? Tendrás que eliminar manualmente la base de datos y el usuario si así lo deseas.",
    "uninstall_warning_3": "También se quedará instalado Python, Node.js y MySQL.",
    "uninstall_press": "Pulsa C para continuar o Q para cancelar",
    "uninstall_done": "Desinstalación completada",
    "up_to_date":'¡TizonaHub está actualizado!'
}
LANG = "en"
sys_lang = locale.getlocale()[0] or ""
if sys_lang.lower().startswith("es"):
    LANG = "es"
else:
    LANG = "en"
langs = {"en": eng, "es": esp}
langData = langs[LANG]

def msg(key):
    return langData.get(key, "")
#FUNCTIONS
def version_to_tuple(v):  
    if isinstance(v, set):
        v = next(iter(v))
    
    if isinstance(v, (list, tuple)):
        v = v[0]

    return str(v)

def printYellow(msg=''):
    print(f'\033[33m{msg}\033[0m')

def printRed(msg=''):
    print(f'\033[31m{msg}\033[0m')

def printGreen(msg=''):
    print(f'\033[32m{msg}\033[0m')
    
def uninstall():
    bin = os.path.expanduser('~/.local/bin')
    exePath = os.path.join(bin, 'tizonahub')

    if os.path.isdir('/opt/TizonaHub'):
        shutil.rmtree('/opt/TizonaHub')

    if os.path.isfile(exePath):
        os.remove(exePath)

    printGreen(msg("uninstall_done"))
def readJSON(filePath):
    with open(filePath, 'r') as file:
        return json.load(file)
    
def getVersion():
    datPath='/etc/tizonahub/data.dat'
    try:
        with open(datPath, "rb") as f:
            data = pickle.load(f)
            clientVersion=data['clientVersion']
            serverVersion=data['serverVersion']
        return {'clientVersion':clientVersion,'serverVersion':serverVersion}
        
    except Exception as e:
        print(e)

def update():
    os.makedirs('/opt/TizonaHub/thubtemp',exist_ok=True)
    datPath='/etc/tizonahub/data.dat'
    clientVersion='0.0.0'
    serverVersion='0.0.0'
    if os.path.isfile(datPath):
        try:
                data=getVersion()
                print(data)
                clientVersion=data['clientVersion']
                serverVersion=data['serverVersion']
            
        except Exception as e:
            print(e)
    zipName = subprocess.check_output([
                "wget",
                "-qO-",
                "https://tizonahub.com/downloads/bundles/tizonahub/latest?data=true"
            ]).decode().strip()
    jsonData=json.loads(zipName)
    latestServerVersion=version_to_tuple(jsonData['serverVersion'])
    latestClientVersion=version_to_tuple(jsonData['clientVersion'])
    serverVersion=version_to_tuple(serverVersion)
    clientVersion=version_to_tuple(clientVersion)
    if latestClientVersion > clientVersion or latestServerVersion > serverVersion:
        name='latestBundle.zip'
        dest=f'/opt/TizonaHub/thubtemp/'
        os.system(f'wget https://tizonahub.com/downloads/installers/ubuntu/latest -O {dest+name}')
        with ZipFile(dest+name,'r') as ref:
            ref.extractall(dest)
        try:
            os.system(f'pm2 stop {startFile}')
        except Exception as e: None
        if os.path.isfile('TizonaInstallerLINUX.py'):
            os.system(f'python3 {'TizonaInstallerLINUX.py'} update')
    else:printGreen(msg('up_to_date'))
    
    exit(1)
#MAIN
if len(args) > 1:
    action = args[1].lower()

    if action == 'uninstall':
        printRed(msg("uninstall_warning_1"))
        inputVal = input()

        if inputVal.lower() == 'c':
            printRed(msg("uninstall_warning_2"))
            printRed(msg("uninstall_warning_3"))
            printRed(msg("uninstall_press"))

            inputVal = input()
            if inputVal.lower() == 'c':
                uninstall()
                exit(1)

        else:
            exit(1)
        

    cmd = None
    match(action):
        case "start":
            cmd = f'pm2 start {startFile} --name tizonahubstart --cwd {os.path.dirname(startFile)}'
        case 'stop':
            cmd = f'pm2 stop {startFile}'
        #case 'autostart':
        #    cmd = f'pm2 startup'
        case 'restart':
            cmd = f'pm2 reload {startFile} && pm2 save'
        case 'update':
            update()
        case 'version': 
            data=getVersion()
            print(f'TizonaServer: {data['serverVersion']}\nTizonaClient: {data['clientVersion']}')
            exit(1)

    os.system(cmd) if cmd else None
