#!/usr/bin/env python3
import tkinter as tk
import ctypes
import glob
import os
import platform
import requests
import shutil
import subprocess
import sys
import time
import msipl_installer
import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from zipfile import ZipFile

# globals
go = False
ostype = platform.system()
if ostype.lower() == 'win32':
    ostype = 'Windows'

if ostype.lower() != 'linux' and ostype.lower() != 'windows' and ostype.lower() != 'darwin':
    print(f'\nERR: Sorry your platform {ostype} is not supported\nSupported platforms are: Linux, Windows, MacOS (Darwin)\n')
    sys.exit(1)

possible_drive = ['-']
windows_disk_letter = {}
deviceID = {}
m=tk.Tk()
m.title('DC-ARK Maker')

# variable setups
var = tk.StringVar(m)
var.set(possible_drive[0])
check = tk.BooleanVar(m)
ipl_only = tk.BooleanVar(m)

disk_check = tk.StringVar(m)
disk_check.set(0)

if ostype.lower() != 'linux' and ostype.lower() != 'darwin':
    import wmi
    import psutil
    c = wmi.WMI()
    for drive in c.Win32_DiskDrive():
        if drive.MediaType == 'Removable Media':
            possible_drive.append('disk'+str(drive.Index))
            deviceID[f'disk{str(drive.Index)}'] = drive.DeviceID
        for part in psutil.disk_partitions():
            if 'removable' in part.opts:
                windows_disk_letter[f'disk{str(drive.Index)}'] = part.mountpoint.split(':')[0]

elif ostype.lower() == 'linux':
    out = subprocess.Popen(["lsblk | awk '{if ($3 == 1 && $1 ~ /^[a-zA-Z]+$/) {print $1}}'"], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)
else:
    out = subprocess.Popen(["""diskutil list external | awk '/external/ { gsub(/\/dev\//, ""); print $1}'"""], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)

def toggle_ipl():

    if ipl_only.get():
        go_check['state'] = 'disabled'
        nw = tk.Toplevel(m) 
        nw.geometry("600x80")
        warn = tk.Label(nw, text="IF YOU LOOKING FOR FULL TM INSTALL DO NOT SELECT THIS!").pack()
        close = tk.Button(nw, text="Close", command=nw.destroy).pack()
        m.update()
    else:
        go_check['state'] = 'normal'
        m.update()

def refresh():
    m.destroy()
    p = sys.executable
    os.execl(p, p, *sys.argv)

def disable_go_check():
    if check.get():
        go_check['state'] = 'disabled'
        check.set(1)
    else:
        go_check['state'] = 'normal'
        check.set(0)

def cleanup() -> None:
    global go
    if go:
        shutil.rmtree("661GO")
        os.remove('661GO.PBP')
        os.remove('661GO.PBP.dec')
    else:
        shutil.rmtree("661")
        os.remove('661.PBP')
        os.remove('661.PBP.dec')
    for f in glob.glob("pspdecrypt*"):
        os.remove(f)

def go_update():
    global go
    if go:
        go = False
        legacy['state'] = 'normal'
    else:
        go = True
        legacy['state'] = 'disabled'

def toggle_run(toggle) -> None:
    if toggle != '-':
        b['state'] = 'normal'
    else:
        b['state'] = 'disabled'

def run() -> None:
    b['state'] = 'disabled'
    x['state'] = 'disabled'
    b['text'] = 'Please Wait...'
    go_check['state'] = 'disabled'
    legacy['state'] = 'disabled'
    ipl_inject_only['state'] = 'disabled'
    global go

    if not ipl_only.get():

        # Download pspdecrypt from John
        if ostype == 'Linux':
            resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-linux.zip', timeout=10, verify=False)
            with open('pspdecrypt-1.0-linux.zip', 'wb') as f:
                f.write(resp.content)
                resp.close()
            with ZipFile('pspdecrypt-1.0-linux.zip', 'r') as zObject:
                zObject.extractall(path=f'{os.getcwd()}/')
            os.system('chmod 755 pspdecrypt')
            x['state'] = 'normal'
        elif ostype == 'Windows':
            resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-windows.zip', timeout=10, verify=False)
            with open('pspdecrypt-1.0-windows.zip', 'wb') as f:
                f.write(resp.content)
                resp.close()
            with ZipFile('pspdecrypt-1.0-windows.zip', 'r') as zObject:
                zObject.extractall(path=f'{os.getcwd()}\\')
            os.system('oschmod 755 pspdecrypt.exe')
            x['state'] = 'normal'
        elif ostype == 'Darwin':
            resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-macos.zip', timeout=10, verify=False)
            with open('pspdecrypt-1.0-macos.zip', 'wb') as f:
                f.write(resp.content)
                resp.close()
            with ZipFile('pspdecrypt-1.0-macos.zip', 'r') as zObject:
                zObject.extractall(path=f'{os.getcwd()}/')
            os.system('oschmod 755 pspdecrypt')
            x['state'] = 'normal'
        else:
            print('\nERR: unsupported platform...\n')
            return

        # Download 6.61 OFW
        if go:
            resp = requests.get('http://du01.psp.update.playstation.org/update/psp/image2/us/2014_1212_fd0f7d0798b4f6e6d32ef95836740527/EBOOT.PBP', timeout=10, verify=False)
            if resp:
                with open('661GO.PBP', 'wb') as f:
                    f.write(resp.content)
                    resp.close()
            else:
                print(resp.status_code)
        else:
            resp = requests.get('http://du01.psp.update.playstation.org/update/psp/image/us/2014_1212_6be8878f475ac5b1a499b95ab2f7d301/EBOOT.PBP', timeout=10, verify=False)
            if resp:
                with open('661.PBP', 'wb') as f:
                    f.write(resp.content)
                    resp.close()
            else:
                print(resp.status_code)

        if ostype == 'Linux' or ostype == 'Darwin':
            if go:
                os.system('./pspdecrypt -e 661GO.PBP')
                shutil.copytree("661GO/F0", "TM/DCARK", dirs_exist_ok=True)
                shutil.copytree("661GO/F1", "TM/DCARK", dirs_exist_ok=True)
            else:
                os.system('./pspdecrypt -e 661.PBP')
                shutil.copytree("661/F0", "TM/DCARK", dirs_exist_ok=True)
                shutil.copytree("661/F1", "TM/DCARK", dirs_exist_ok=True)
        else:
            if go:
                os.system('.\\pspdecrypt.exe -e 661GO.PBP')
                shutil.copytree("661GO\\F0\\", "TM\\DCARK\\", dirs_exist_ok=True)
                shutil.copytree("661GO\\F1\\", "TM\\DCARK\\", dirs_exist_ok=True)
            else:
                os.system('.\\pspdecrypt.exe -e 661.PBP')
                shutil.copytree("661\\F0\\", "TM\\DCARK\\", dirs_exist_ok=True)
                shutil.copytree("661\\F1\\", "TM\\DCARK\\", dirs_exist_ok=True)

    # Download msipl_installer from Draan (forked for macOS support)
    #resp = requests.get('https://raw.githubusercontent.com/krazynez/msipl_installer/main/msipl_installer.py', verify=False)
    #with open('msipl_installer.py', 'wb') as f:
        #f.write(resp.content)

    if ostype == 'Linux':
        disk = var.get() + '1'
        get_mountpoint = subprocess.Popen(f"lsblk | awk '/{disk}/ {{print $7}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        if not ipl_only.get():
            shutil.copytree("TM", get_mountpoint, dirs_exist_ok=True)
        msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, None, False, True ))
        if check.get():
            msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'tm_msipl_legacy.bin', False, False ))
        else:
            msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'msipl.bin', False, False ))
        status.config(fg='green', text="DONE!")
    elif ostype == 'Darwin':
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{var.get()}'])
        subprocess.run(['sync'])
        time.sleep(2)
        if check.get():
            msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'tm_msipl_legacy.bin', False, False ))
        else:
            msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'msipl.bin', False, False ))
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{var.get()}'])
        subprocess.run(['mkdir', '/Volumes/__psp__'])
        get_mountpoint = '/Volumes/__psp__'
        copypoint = get_mountpoint + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        subprocess.run(['mount', '-t', 'msdos', '-o', 'rw', f'/dev/{var.get()}s1', get_mountpoint])
        if not ipl_only.get():
            shutil.copytree("TM", f"{copypoint}", dirs_exist_ok=True)
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{var.get()}'])
        status.config(fg='green', text="DONE!")
    else:
        get_mountpoint = windows_disk_letter[var.get()] + ":\\TM\\"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        if not ipl_only.get():
            shutil.copytree("TM", f"{get_mountpoint}", dirs_exist_ok=True)
        #os.system('oschmod 755 msipl_installer.py')
        #os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[var.get()][-1])} --clear')
        #os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[var.get()][-1])} --insert msipl.bin')
        msipl_installer.main(msipl_installer.Args(f'{int(deviceID[var.get()][-1])}', False, None, False, True ))
        if check.get():
            msipl_installer.main(msipl_installer.Args(f'{int(deviceID[var.get()][-1])}', False, 'tm_msipl_legacy.bin', False, False ))
        else:
            msipl_installer.main(msipl_installer.Args(f'{int(deviceID[var.get()][-1])}', False, 'msipl.bin', False, False ))
        status.config(fg='green', text="DONE!")

        b['text'] = 'DONE!'
    x['state'] = 'normal'

    if not ipl_only.get():
        cleanup()

if ostype == 'Linux' or ostype == 'Darwin':
    if os.geteuid() != 0:
        print('\nSorry this needs to run as root/admin!\n')
        sys.exit(1)
else:
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        print('\nSorry this needs to run as root/admin!\n')
        sys.exit(1)

# Setup
m.minsize(320, 230)

disk = tk.OptionMenu(m, var, *possible_drive, command=toggle_run)
disk.grid(row=0,column=1)
tk.Label(text="Select PSP/Memory Stick:", width=25).grid(row=0, column=0)
status = tk.Label(fg='red', text="PLEASE VERIFY\nDISK BEFORE CONTINUING!", width=25)
status.grid(row=1, column=0)

#internal=tk.Checkbutton(m, text='Show Internal Disk', variable=disk_check, onvalue=1, offvalue=0)
#internal.grid(row=3, column=1)

go_check=tk.Checkbutton(m, text='PSP Go Model (ONLY!)', command=go_update)
go_check.grid(sticky="W", row=3, column=0)

legacy=tk.Checkbutton(m, text="Legacy IPL (1000s and early 2000s ONLY!)", variable=check, command=disable_go_check)
legacy.grid(row=4, column=0)

b=tk.Button(m, text='Run', command=run)
b.grid(row=1,column=1)
r=tk.Button(m, text='Refresh', command=refresh)
r.grid(row=6, column=0, sticky='S')

x=tk.Button(m, text='Exit', command=m.destroy)
x.grid(row=2,column=1)

if var.get() == '-':
    b['state'] = 'disabled'

ipl_inject_only=tk.Checkbutton(m, text='Inject IPL (ONLY!)', variable=ipl_only, command=toggle_ipl)
ipl_inject_only.grid(row=2, column=0, sticky='W')

m.mainloop()
