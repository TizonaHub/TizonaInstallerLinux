import subprocess
import os
import random
from getpass import getpass
from zipfile import ZipFile
import json
import operator
from time import sleep
import re
import sys

nvm_env=r'''export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 
                [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'''
needNvm_env=False
bundleURI='192.168.1.127:8000/downloads/bundles/tizonahub/latest'
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
    '''    print(version)
    print(op)
    print(expected)'''

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

'''
MAIN EXECUTION
'''
runAs()
print('\033[32mWelcome to TizonaHub installer\033[0m')
printRed(asciiArt)

pkgmgr = detectPackageManager()
if not pkgmgr:
    print('\033[31mYour Linux distribution is not supported automatically.\033[0m')
    exit(1)


# MySQL
MySQLVersion = check('mysql')
if not MySQLVersion:
    installMySQL = input('\033[33mMySQL was not detected. Install it? [y/n] \033[0m').strip().lower()
    if installMySQL == 'y':
        install('mysql-server')
        MySQLVersion = check('mysql')
        if MySQLVersion:
            print('\033[32mMySQL installed successfully\033[0m')
        else:
            print('\033[31mMySQL installation failed.\033[0m')
else:
    print('\033[32mMySQL was detected\033[0m')

# Node.js

NodeVersion = checkNode()
if not NodeVersion:
    installNode = input('\033[33mNode.js was not detected. Install it? [y/n] \033[0m').strip().lower()
    if installNode == 'y':
        installNodeFn()
        NodeVersion = checkNode()
    else:
        print("\033[35mNode.js must be installed. To complete TizonaHub's installation, please install Node.js \033[0m")
else:
    print('\033[32mNode.js was detected\033[0m')



if not NodeVersion:
    print("\033[35mNode.js must be installed. To complete TizonaHub's installation, please install Node.js \033[0m")
    exit(1)

# Install Tizona
printGreen('Downloading latest TizonaHub bundle...')

subprocess.run(
    ['wget', bundleURI, '-O', bundlePath],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
printGreen('Unzipping bundle...')
unzipRelease(bundlePath)

#Ask for data
dbName = input('Database name: ')
dbUser = input('User: ')
dbPassword = getpass()

requirements=getRequirements()
print('Requirements: ', requirements)
nodeReqs=requirements['node'].split(' ')
pythonReqs=requirements['python'].split(' ')
mysqlReqs=requirements['mysql'].split(' ')

def comparingTask(depVer,depRequirements,depName):
    condition1=len(depRequirements) >=1 and not compareVersions(depVer,getVersion(depRequirements[0]),getOperator(depRequirements[0]))
    condition2=len(depRequirements) >=2 and not compareVersions(depVer,getVersion(depRequirements[1]),getOperator(depRequirements[1]))

    if condition1:  
        print(f"\033[33mExpected {depName} version: {depRequirements[0]}, your current version: {depVer}\033[0m")
        print(f"\033[33mTizonaHub may not work correctly\033[0m")
        return
    elif condition2:
        print(f"\033[33mExpected {depName} version: {depRequirements[1]}, your current version: {depVer}\033[0m")
        print(f"\033[33mTizonaHub may not work correctly\033[0m")
        return
    else: 
        printGreen(f'Expected {depName} version: {depRequirements[0]}, your current version: {depVer}')
        return

#COMPARING VERSIONS
comparingTask(NodeVersion,nodeReqs,'Node.js')
comparingTask(MySQLVersion,mysqlReqs,'MySQL')
comparingTask(check('python3'),pythonReqs,'Python')


#Installing dependencies
if NodeVersion:
    installDependencies('/opt/TizonaHub/TizonaServer/')
    installDependencies('/opt/TizonaHub/TizonaServer/','npm install -g pm2')
else:
    printRed('Since no Node installation was not found, you will need to use "npm install" by yourself')
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
        'DB_PASSWORD': dbPassword,
        'DB': dbName,
        'ORIGINS': '["*"]'
    })

    with open(env_path, 'w') as envFile:
        for key, value in splitContent.items():
            envFile.write(f'{key}={value}\n')
    os.rename(env_path, '/opt/TizonaHub/TizonaServer/.env')
    print('\033[32m.env file generated\033[0m')
else:
 generateEnv(dbName,dbPassword,dbUser)



#Remove remaining files & dirs
if os.path.isfile('/opt/TizonaHubBundleLatest.zip'): os.remove('/opt/TizonaHubBundleLatest.zip')

print()
print('======')
print('\033[32mTizonaHub was installed successfully!\033[0m')
printGreen('To setup a new database, log into mysql shell using sudo mysql and execute the following commands:')
printGreen()
printYellow("CEATE DATABASE your_db_name:")
printYellow()
printYellow("USE your_db_name;")
printYellow()
printYellow("source /opt/TizonaHub/TizonaServer/SQL/setup.sql;")
printYellow()
printYellow("CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';")
printYellow()
printYellow("GRANT ALL PRIVILEGES ON *.* TO 'your_user'@'localhost';")
printYellow()
printYellow("FLUSH PRIVILEGES;")



