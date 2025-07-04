import os
import shutil
import subprocess

srcdir = os.path.dirname(__file__)+'/src'
image = srcdir+'/sImages'
code = srcdir+'/sCode'
other = srcdir+'/sOther'
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
V = "\033[95m"
S = "\033[0m"

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



print(f"{B}-------------- Stage 1: Removing App data -------------------{S}")
Remove()
