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

def Copy():
    try:
        shutil.copytree(image,'/usr/share/NikoruDE/Image')
        shutil.copytree(other,'/usr/share/NikoruDE/Other')
        shutil.copytree(code,'/usr/share/NikoruDE/Code')
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


def RunProc(process,cwd = None):
    result = subprocess.run(process,capture_output=True,text=True,cwd=cwd)
    if result.stderr == None or result.returncode == 0:
        print(G+result.stdout+S)
        print(Y+result.stderr+S)
        print(f"state: [{G}OK{S}]")
    else:
        print(R+result.stderr+S)
        print(f"state: [{Y}SKIP{S}]")
        

        

print(f"{B}-------------- Stage 1: Removing old App data ---------------{S}")
Remove()
print(f"{B}-------------- Stage 2: Copy App to device ------------------{S}")
Copy()
print(f"{B}-------------- Stage 3: Restore Context ---------------------{S}")
RunProc(['sudo','restorecon','-R','-v','/usr/share/NikoruDE'])
