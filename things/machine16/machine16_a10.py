import json, requests, types
base = "https://raw.githubusercontent.com/Coxinha2K/Project16/main"
code = requests.get(f"{base}/things/retrofs/retrofs_alpha.py").text
name = "rfs"
rfs = types.ModuleType(name)
exec(code, rfs.__dict__)

class Kernel:
    def __init__(self, compiled_krnl):
        self.krnl = compiled_krnl
        
    def run(self, function, args):
        np = {}
        krnl = exec(self.krnl, np)
        try:
            func = np.get(function)
        except Exception as e:
            print(f"Machine16: failed to run function {function}(): {e}")
            exit()
            
      
        func(args)
        
fs = rfs.Filesystem(name="Machine16")
file = "Project16.rfs"
fs.importfs(file)
try:
    bootargs = json.loads(fs.catfile("P0", "/system/config/boot.cfg"))
except Exception as e:
    print(f"Machine16: failed to load boot arguments: {e}")
    exit()
    
krnl_path = bootargs["Core16"]["Path"].split("@")
try:
    kernel = fs.catfile(krnl_path[1], krnl_path[0])
except Exception as e:
    print(f"Machine16: failed to read kernel: {e}")
    exit()
    
np = {}
compiled_krnl = compile(kernel, "<Core16>", "exec")
exec(compiled_krnl, np)
if "core16boot" not in np:
    print(f"Machine16: failed to read kernel: 'core16boot' not in namespace")
    exit()
    
# bootargs["Core16"]["Debug"] = True
# bootargs["Project16"]["CSRE"]["CSREEnabled"] = False
fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))
krnl = Kernel(compiled_krnl)
try:
    krnl.run("core16boot", (bootargs, fs))
except:
    bootargs["Project16"]["CSRE"]["CSREEnabled"] = True
    fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))
    
fs.exportfs(file=file)
