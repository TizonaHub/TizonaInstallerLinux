import subprocess
import os
import random
from getpass import getpass
from zipfile import ZipFile
import json
import operator
from time import sleep
import re
import pickle
import sys
import locale

#LANG
eng = {
    "welcome": "Welcome to TizonaHub installer",
    "unsupported": "Your Linux distribution is not supported automatically.",
    "mysql_not_detected": "MySQL was not detected. Install it? [y/n] ",
    "mysql_installed": "MySQL installed successfully",
    "mysql_failed": "MySQL installation failed.",
    "mysql_detected": "MySQL was detected",
    "node_not_detected": "Node.js was not detected. Install it? [y/n] ",
    "node_required": "Node.js must be installed. To complete TizonaHub's installation, please install Node.js",
    "node_detected": "Node.js was detected",
    "downloading_bundle": "Downloading latest TizonaHub bundle...",
    "unzipping_bundle": "Unzipping bundle...",
    "db_name": "Database name: ",
    "db_user": "User: ",
    "requirements": "Requirements: ",
    "exp_node": "Expected Node.js version: ",
    "exp_mysql": "Expected MySQL version: ",
    "exp_python": "Expected Python version: ",
    "may_not_work": "TizonaHub may not work correctly",
    "no_node_manual": "Since no Node installation was not found, you will need to use \"npm install\" by yourself",
    "env_generated": ".env file generated",
    "installed_ok": "TizonaHub was installed successfully!",
    "setup_mysql": "To setup a new database, log into mysql shell using sudo mysql and execute the following commands:",
    "press_s": "Press the S key to view prepared queries or Q to quit. Press Enter to confirm"
}

esp = {
    "welcome": "Bienvenido al instalador de TizonaHub",
    "unsupported": "Tu distribución de Linux no es compatible automáticamente.",
    "mysql_not_detected": "MySQL no fue detectado. ¿Instalarlo? [y/n] ",
    "mysql_installed": "MySQL se instaló correctamente",
    "mysql_failed": "La instalación de MySQL falló.",
    "mysql_detected": "MySQL fue detectado",
    "node_not_detected": "Node.js no fue detectado. ¿Instalarlo? [y/n] ",
    "node_required": "Debe instalarse Node.js. Para completar la instalación de TizonaHub, instala Node.js",
    "node_detected": "Node.js fue detectado",
    "downloading_bundle": "Descargando el paquete más reciente de TizonaHub...",
    "unzipping_bundle": "Descomprimiendo paquete...",
    "db_name": "Nombre de base de datos: ",
    "db_user": "Usuario: ",
    "requirements": "Requisitos: ",
    "exp_node": "Versión requerida de Node.js: ",
    "exp_mysql": "Versión requerida de MySQL: ",
    "exp_python": "Versión requerida de Python: ",
    "may_not_work": "TizonaHub podría no funcionar correctamente",
    "no_node_manual": "Como no se detectó Node, deberás usar \"npm install\" manualmente",
    "env_generated": "Archivo .env generado",
    "installed_ok": "¡TizonaHub se instaló correctamente!",
    "setup_mysql": "Para configurar una base de datos nueva, entra a MySQL con sudo mysql y ejecuta:",
    "press_s": "Presiona la tecla S para ver las consultas preparadas o Q para salir. Pulsa Enter para confirmar"
}

LANG = "en"
sys_lang = locale.getlocale()[0] or ""

if sys_lang.lower().startswith("es"):
    LANG = "es"
else:
    LANG = "en"

langs = {"en": eng, "es": esp}
langData = langs[LANG]

installerVersion='0.4.0'

nvm_env=r'''export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 
                [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'''
needNvm_env=False
bundleURI='https://tizonahub.com/downloads/bundles/tizonahub/latest'
bundlePath='/opt/TizonaHubBundleLatest.zip'
asciiArt='''
  #############################%% 
#############################%%%%%
#######################%%%%%%%%%%%
##################:     =%%%%%%%%%
###########*-::--         +%%%%%%%
#########*                 *%%%%%%
#####*:                     :#%%%%
####-                         #%%%
####:                         #%%%
####-                        +%%%%
######:                    -%%%%%%
######%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%           
'''

def genRandomString():
    chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>1234567890¿?=)(%$·#@}{*,.:;-_'
    string=''
    for i in range(78):
        string=string+chars[random.randint(0,len(chars)-1)]
    return string    

#Functions
def printYellow(msg=''):
    print(f'\033[33m{msg}\033[0m')

def printRed(msg=''):
    print(f'\033[31m{msg}\033[0m')

def printGreen(msg=''):
    print(f'\033[32m{msg}\033[0m')

def unzipRelease(zipName):
    with ZipFile(zipName,'r') as ref:
        ref.extractall('/opt/TizonaHub')

def genRandomString():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>1234567890¿?=)(%$·#@}{*,.:;-_'
    return ''.join(random.choices(chars, k=78))

def runAs():
    if os.geteuid() !=0:
        os.execvp('sudo',["sudo",sys.executable] + sys.argv)
def check(cmd):
    try:
            result=subprocess.run([cmd, '--version'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return getVersion(result.stdout.strip())
    except:
        return False

def checkNode():
    global needNvm_env
    try:
        result=subprocess.run(['node --version'],check=True,capture_output=True,text=True)
        return getVersion(result.stdout.strip())
    except:
        None
    try:
        result=subprocess.run(['bash','-c','source ~/.nvm/nvm.sh && node --version'],check=True,capture_output=True,text=True)
        needNvm_env=True
    except:
        return False
    
    return getVersion(result.stdout.strip())


def detectPackageManager():
    if os.path.exists('/etc/debian_version'):
        return 'apt'
    else:
        return None

def install(package):
    print(f'\033[34mInstalling {package}...\033[0m')
    try:
        if pkgmgr == 'apt':
            subprocess.run(['sudo', 'apt', 'update'])
            subprocess.run(['sudo', 'apt', 'install', '-y', package])
        else:
            print('Unsupported package manager.')
    except Exception as e:
        print(f'\033[31mFailed to install {package}: {e}\033[0m')


def installNodeFn():
    global needNvm_env
    if not check('curl'):install('curl')
    try:
        subprocess.run('curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash', shell=True, check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
        command = r'''
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 
                [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
                nvm install --lts
                '''
        subprocess.run(command, check=True, executable='/bin/bash',shell=True, )
        needNvm_env=True
        print('\033[32mNode.js installed successfully\033[0m')
    except subprocess.CalledProcessError as e:
        print('\033[31mCould not install Node.js:\033[0m')
        print(e)

def getOperator(str):
    if isinstance(str, bytes):
        str=str.decode('utf-8')

    match=re.search(r'(>=|<=|==|!=|<|>)',str)
    
    if match:
        return match.group(0)
    return None


def getVersion(str):
    if isinstance(str, bytes):
        str=str.decode('utf-8')

    match=re.search(r'v?(\d+\.\d+\.\d+)',str)
    
    if match:
        return match.group(1)
    return None

def readJSON(filePath):
 with open(filePath,'r') as file:
     return json.load(file)
 
def getRequirements():
    content = readJSON('/opt/TizonaHub/TizonaServer/package.json')
    engines=content['engines']
    return engines

#Changes folder name from program + version tag to just program name. Example: TizonaServer-0.3.0 -> TizonaServer
def compareVersions(version,expected,op):
    if not version or not expected: return None

    versionList=[int(x) for x in version.split('.')]
    expectedList=[int(x) for x in expected.split('.')]

    #Sets same length "[xx.x] = [xx.xx.xx]"
    versionList += [0] * (3 - len(versionList))
    expectedList += [0] * (3 - len(expectedList))
    ops={
        '>':operator.gt,
        '>=':operator.ge,
        '<':operator.lt,
        '<=':operator.le,
        '==':operator.ge,
        '!=':operator.ne
    }
    
    op_func=ops[op]
    return (op_func(versionList,expectedList))

def generateEnv(dbName,dbPassword,dbUser):
    dict={
        "PASSPHRASE":"",
        "CRT":"",
        "SS_KEY":"",
        "JWT_KEY":genRandomString(),
        "ORIGINS":"["+'"*"'+"]",
        "DB_HOST":'127.0.0.1',
        "DB_USER":dbUser,
        "DB_USER_PASSWORD":dbPassword,
        "DB":dbName,
        "STATIC":"storage",
        "NODE_ENV":"production"
    }
    text=''
    for elem in dict:
        value='""' if len(dict[elem])==0 else str(dict[elem])
        text+= elem+'='+value+"\n"
    try:
        with open(os.path.abspath('/opt/TizonaHub/TizonaServer/.env'),"w") as file:
            file.write(text)
    except Exception as e:
        printRed('Could not write .env file: ',e)

def installDependencies(cwd,cmd='npm install'):
    npmSource='source ~/.nvm/nvm.sh && '
    fullPrompt=['npm install'] if not needNvm_env else ['bash','-c',npmSource+cmd]
    subprocess.run(fullPrompt,check=True,capture_output=True,text=True,cwd=cwd)

def setProgramData():

        app_data_dir = os.path.join("/etc/TizonaHub")
        os.makedirs(app_data_dir, exist_ok=True)

        data_file = os.path.join(app_data_dir, "data.dat")
        clientJSON=False
        serverJSON=False
        try:
            clientJSONPath='/opt/TizonaHub/TizonaServer/dist/package.json'
            serverJSONPath='/opt/TizonaHub/TizonaServer/package.json'
            if os.path.isfile(clientJSONPath): clientJSON=readJSON(clientJSONPath) 
            if os.path.isfile(serverJSONPath): serverJSON=readJSON(serverJSONPath)
        except Exception as e:
            None

        clientVersion=clientJSON['version'] if clientJSON else '0.0.0'
        serverVersion=serverJSON['version'] if serverJSON else '0.0.0'
        data = {
            "installerVersion": {installerVersion},
            "clientVersion":    {clientVersion},
            "serverVersion":    {serverVersion}
            }
        with open(data_file, "wb") as f:
            pickle.dump(data, f)

'''
MAIN EXECUTION
'''
runAs()
printGreen(langData["welcome"])
printRed(asciiArt)

pkgmgr = detectPackageManager()
if not pkgmgr:
    printRed(langData["unsupported"])
    exit(1)

# MySQL
MySQLVersion = check('mysql')
if not MySQLVersion:
    installMySQL = input(printYellow(langData["mysql_not_detected"]) or "").strip().lower()
    if installMySQL == 'y':
        install('mysql-server')
        MySQLVersion = check('mysql')
        if MySQLVersion:
            printGreen(langData["mysql_installed"])
        else:
            printRed(langData["mysql_failed"])
else:
    printGreen(langData["mysql_detected"])

# Node.js

NodeVersion = checkNode()
if not NodeVersion:
    installNode = input(printYellow(langData["node_not_detected"]) or "").strip().lower()
    if installNode == 'y':
        installNodeFn()
        NodeVersion = checkNode()
    else:
        printYellow(langData["node_required"])
else:
    printGreen(langData["node_detected"])

if not NodeVersion:
    printYellow(langData["node_required"])
    exit(1)

# Install Tizona
printGreen(langData["downloading_bundle"])

subprocess.run(
    ['wget', bundleURI, '-O', bundlePath],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
printGreen(langData["unzipping_bundle"])
unzipRelease(bundlePath)

#Ask for data
dbName = input(langData["db_name"])
dbUser = input(langData["db_user"])
dbPassword = getpass()

requirements=getRequirements()
print(langData["requirements"], requirements)
nodeReqs=requirements['node'].split(' ')
pythonReqs=requirements['python'].split(' ')
mysqlReqs=requirements['mysql'].split(' ')

def comparingTask(depVer,depRequirements,depName, key):
    condition1=len(depRequirements) >=1 and not compareVersions(depVer,getVersion(depRequirements[0]),getOperator(depRequirements[0]))
    condition2=len(depRequirements) >=2 and not compareVersions(depVer,getVersion(depRequirements[1]),getOperator(depRequirements[1]))

    if condition1:  
        printYellow(f"{langData[key]}{depRequirements[0]}, your current version: {depVer}")
        printYellow(langData["may_not_work"])
        return
    elif condition2:
        printYellow(f"{langData[key]}{depRequirements[1]}, your current version: {depVer}")
        printYellow(langData["may_not_work"])
        return
    else: 
        printGreen(f"{langData[key]}{depRequirements[0]}, your current version: {depVer}")
        return

#COMPARING VERSIONS
comparingTask(NodeVersion,nodeReqs,'Node.js',"exp_node")
comparingTask(MySQLVersion,mysqlReqs,'MySQL',"exp_mysql")
comparingTask(check('python3'),pythonReqs,'Python',"exp_python")

#Installing dependencies
if NodeVersion:
    installDependencies('/opt/TizonaHub/TizonaServer/')
    installDependencies('/opt/TizonaHub/TizonaServer/','npm install -g pm2')
else:
    printRed(langData["no_node_manual"])
    sleep(2)
# .env setup
env_path = "/opt/TizonaHub/TizonaServer/.env.example"
if not os.path.isfile(env_path):
    if os.path.isfile("/opt/TizonaHub/TizonaServer/.env"):
        env_path="/opt/TizonaHub/TizonaServer/.env"
    else: env_path=None

if env_path:
    with open(env_path, "r") as envFile:
        content = [line.strip() for line in envFile.readlines() if line.strip()]

    splitContent = dict(line.split('=', 1) for line in content)
    splitContent.update({
        'JWT_KEY': genRandomString(),
        'DB_USER': dbUser,
        'DB_USER_PASSWORD': dbPassword,
        'DB': dbName,
        'ORIGINS': '["*"]'
    })

    with open(env_path, 'w') as envFile:
        for key, value in splitContent.items():
            envFile.write(f'{key}={value}\n')
    os.rename(env_path, '/opt/TizonaHub/TizonaServer/.env')
    printGreen(langData["env_generated"])
else:
 generateEnv(dbName,dbPassword,dbUser)

#Remove remaining files & dirs
if os.path.isfile('/opt/TizonaHubBundleLatest.zip'): os.remove('/opt/TizonaHubBundleLatest.zip')

setProgramData()

#Handle service
bin= os.path.expanduser('~/.local/bin')
exePath=os.path.join(bin,'tizonahub')
bashrc = os.path.expanduser("~/.bashrc")

os.makedirs(bin, exist_ok=True)
os.makedirs('/opt/TizonaHub/Terminal/', exist_ok=True)

with open(exePath, "w", encoding="utf-8") as f: #EXE
    f.write("""
#!/bin/bash
cd /opt/TizonaHub/Terminal/
python3 terminal.py "$@"
""")
with open("/opt/TizonaHub/Terminal/terminal.py", "w", encoding="utf-8") as f: #PYTHON
    f.write("""
import sys
import os
import shutil
import json
import locale

args = sys.argv
startFile = '/opt/TizonaHub/TizonaServer/start.js'

# LANG
eng = {
    "uninstall_warning_1": "You are about to uninstall TizonaHub, press C to continue or Q to cancel",
    "uninstall_warning_2": "Are you sure? You will have to manually remove the database and the user if you wish.",
    "uninstall_warning_3": "Python, Node.js and MySQL will remain installed.",
    "uninstall_press": "Press C to continue or Q to cancel",
    "uninstall_done": "Uninstallation completed"
}
esp = {
    "uninstall_warning_1": "Estás a punto de desinstalar TizonaHub, pulsa C para continuar o Q para cancelar",
    "uninstall_warning_2": "¿Estás seguro? Tendrás que eliminar manualmente la base de datos y el usuario si así lo deseas.",
    "uninstall_warning_3": "También se quedará instalado Python, Node.js y MySQL.",
    "uninstall_press": "Pulsa C para continuar o Q para cancelar",
    "uninstall_done": "Desinstalación completada"
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
        case 'start':
            cmd = f'pm2 start {startFile}'
        case 'stop':
            cmd = f'pm2 stop {startFile}'
        case 'autostart':
            cmd = f'pm2 startup {startFile}'
        case 'restart':
            cmd = f'pm2 reload {startFile} && pm2 save'

    os.system(cmd)

""")
    
bashrcContent='export PATH="$HOME/.local/bin:$PATH"'
with open(bashrc, "r", encoding="utf-8") as f: # MAKES EXE AVAILABLE ON TERMINAL
    content = f.read()
    if bashrcContent not in content:
        with open(bashrc, "a", encoding="utf-8") as f:
            f.write(f'\n{bashrcContent}\n')    

os.system(f'chmod +x {exePath}')

print()
print('======')
printGreen(langData["installed_ok"])
printGreen(langData["setup_mysql"])
print()
printYellow("CREATE DATABASE your_db_name;")
print()
printYellow("USE your_db_name;")
print()
printYellow("source /opt/TizonaHub/TizonaServer/SQL/setup.sql;")
print()
printYellow("CREATE USER 'your_db_user'@'localhost' IDENTIFIED BY 'your_db_password';")
print()
printYellow("GRANT ALL PRIVILEGES ON *.* TO 'your_db_user'@'localhost';")
print()
printYellow("FLUSH PRIVILEGES;")

if len(dbName)>2 and len(dbUser)>2:
    printGreen(langData["press_s"])
    preparedQuery=f"CREATE DATABASE {dbName};USE {dbName};source /opt/TizonaHub/TizonaServer/SQL/setup.sql;CREATE USER '{dbUser}'@'localhost' IDENTIFIED BY '{dbPassword}';GRANT ALL PRIVILEGES ON *.* TO '{dbUser}'@'localhost';FLUSH PRIVILEGES;"
    inputVal=input()
    if inputVal.lower() == 's': print(preparedQuery)
