import subprocess
import os
import random
from getpass import getpass

def genRandomString():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>1234567890¿?=)(%$·#@}{*,.:;-_'
    return ''.join(random.choices(chars, k=78))

def check(cmd):
    try:
        subprocess.run([cmd, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def detectPackageManager():
    if os.path.exists('/etc/debian_version'):
        return 'apt'
    elif os.path.exists('/etc/arch-release'):
        return 'pacman'
    elif os.path.exists('/etc/redhat-release'):
        return 'dnf'
    elif os.path.exists('/etc/SuSE-release'):
        return 'zypper'
    else:
        return None

def install(pkgmgr, package):
    print(f'\033[34mInstalling {package} with {pkgmgr}...\033[0m')
    try:
        if pkgmgr == 'apt':
            subprocess.run(['sudo', 'apt', 'update'])
            subprocess.run(['sudo', 'apt', 'install', '-y', package])
        elif pkgmgr == 'dnf':
            subprocess.run(['sudo', 'dnf', 'install', '-y', package])
        elif pkgmgr == 'pacman':
            subprocess.run(['sudo', 'pacman', '-Syu', package, '--noconfirm'])
        elif pkgmgr == 'zypper':
            subprocess.run(['sudo', 'zypper', 'install', '-y', package])
        else:
            print('Unsupported package manager.')
    except Exception as e:
        print(f'\033[31mFailed to install {package}: {e}\033[0m')

def installNodeFn():
    os.system('curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash')
    result = subprocess.run('bash -c "source ~/.nvm/nvm.sh && node -v"', shell=True)

    if result.returncode == 0:
        print('\033[32mNode was installed successfully\033[0m')
    else:
        print('\033[31mNode installation failed\033[0m')


'''
MAIN EXECUTION
'''
print('\033[32mWelcome to TizonaHub installer\033[0m')

pkgmgr = detectPackageManager()
if not pkgmgr:
    print('\033[31mYour Linux distribution is not supported automatically.\033[0m')
    exit(1)

# Check required tools
if not check('unzip'):
    install(pkgmgr, 'unzip')

installClient = input('Would you like to install TizonaClient? [y/n] ').strip().lower() == 'y'

# MySQL
MySQLExists = check('mysql')
if not MySQLExists:
    installMySQL = input('\033[33mMySQL was not detected. Install it? [y/n] \033[0m').strip().lower()
    if installMySQL == 'y':
        install(pkgmgr, 'mysql-server')
        MySQLExists = check('mysql')
        if MySQLExists:
            print('\033[32mMySQL installed successfully\033[0m')
        else:
            print('\033[31mMySQL installation failed.\033[0m')
else:
    print('\033[32mMySQL was detected\033[0m')

# Node.js
NodeExists = check('node')
if not NodeExists:
    installNode = input('\033[33mNode.js was not detected. Install it? [y/n] \033[0m').strip().lower()
    if installNode == 'y':
        installNodeFn(pkgmgr)
else:
    print('\033[32mNode.js was detected\033[0m')

# Install Tizona
print('\033[32mInstalling TizonaServer...\033[0m')
os.system('unzip TizonaServerRelease_v0.3.0.zip -d TizonaServer')

if installClient:
    print('\033[32mInstalling TizonaClient...\033[0m')
    os.system('unzip TizonaClientRelease_v0.3.0.zip -d TizonaServer/dist')

# .env setup
db = input('Database name: ')
dbUser = input('User: ')
dbPassword = getpass()

env_path = "TizonaServer/.env.example"
with open(env_path, "r") as envFile:
    content = [line.strip() for line in envFile.readlines() if line.strip()]

splitContent = dict(line.split('=', 1) for line in content)
splitContent.update({
    'JWT_KEY': genRandomString(),
    'DB_USER': dbUser,
    'DB_PASSWORD': dbPassword,
    'DB': db,
    'ORIGINS': '["*"]'
})

with open(env_path, 'w') as envFile:
    for key, value in splitContent.items():
        envFile.write(f'{key}={value}\n')

os.rename('TizonaServer/.env.example', 'TizonaServer/.env')
print('\033[32m.env file generated\033[0m')
print('\033[32mTizonaHub was installed successfully\033[0m')