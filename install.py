# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import shutil
import subprocess

srcdir = os.path.dirname(__file__)+'/src'
code = srcdir+'/sCode'
other = srcdir+'/sOther'
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
V = "\033[95m"
S = "\033[0m"

def Copy():
    try:
        shutil.copytree(other,'/usr/share/NikoruDE/Other')
        shutil.copytree(code,'/usr/share/NikoruDE/Code')
        shutil.rmtree('/usr/share/NikoruDE/Code/modules')
        print(f"state: [{G}OK{S}]")
    except Exception as e:
        print(R+str(e)+S)
        print(f"state: [{R}ERR{S}]")
        exit(1)
    
def Remove():
    try:
        shutil.rmtree('/usr/share/NikoruDE')
        print(f"state: [{G}OK{S}]")
    except Exception as e:
        if not isinstance(e,FileNotFoundError):
            print(R+str(e)+S)
            print(f"state: [{R}ERR{S}]")
            exit(1)
        else:
            print(f"state: [{G}SKIP{S}]")


def RunProc(process,cwd = None,skiperror = False):
    result = subprocess.run(process,capture_output=True,text=True,cwd=cwd)
    if result.stderr == None or result.returncode == 0:
        print(G+result.stdout+S)
        print(Y+result.stderr+S)
        print(f"state: [{G}OK{S}]")
    else:
        if skiperror:
            print(R+result.stderr+S)
            print(f"state: [{Y}SKIP{S}]")
        else:
            print(R+result.stderr+S)
            print(f"state: [{R}ERR{S}]")
            exit(1)
        
def RPrem():
    try:
        for froot, dirs, files in os.walk('/usr/share/NikoruDE'):
            for dir in dirs:
                drPath = os.path.join(froot,dir)
                print(f'{V}Dir:{drPath} {S}')
                os.chmod(drPath,0o755)
        
            for file in files:
                flPath = os.path.join(froot,file)
                if file.endswith('.py'):
                    print(f'{G}File exec:{flPath} {S}')
                    os.chmod(flPath,0o755)
                else:
                    print(f'{V}File:{flPath} {S}')
                    os.chmod(flPath,0o755)
                
        print(f"state: [{G}OK{S}]")
    except Exception as e:
        print(R+str(e)+S)
        print(f"state: [{R}ERR{S}]")
        exit(1)
    


        

print(f"{B}-------------- Stage 1: Removing old App data ---------------{S}")
Remove()
print(f"{B}-------------- Stage 2: Copy App to device ------------------{S}")
Copy()
print(f"{B}-------------- Stage 3: Restore premissions -------------------------{S}")
RPrem()
print(f"{B}-------------- Stage 4: Restore Context ---------------------{S}")
RunProc(['sudo','restorecon','-R','-v','/usr/share/NikoruDE'],skiperror=True)
print(f"{V}------- State: [{G}SUCCES{V}]{G} Instalation Complete{V} ----------{S}")
