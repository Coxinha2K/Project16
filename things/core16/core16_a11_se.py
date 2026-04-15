import time
class QuitCSRE(Exception):
    pass

class Kernel:
    def __init__(self, fs):
        self.fs = fs
        
    def read_fs(self):
        return self.fs
    
    
def core16boot(args):
    bootargs = args[0]
    fs = args[1]
    debug = bootargs["Core16"]["Debug"]
    if debug:
        print("[Core16] Project16 Core16 SE, version A11")
        print("[Core16] Loading filesystem")
    import json, types
    if debug:
        print("[Core16] Preparing VRAM...")
    if bootargs["ResetVRAM"]:
        fs.format("P2", "RAM")
    else:
        if debug:
            print("[Core16] Note: ResetVRAM=False, unable to reset VRAM")
    
    fs.mkfile("P2", "/boot/power", "On")
    if bootargs["Project16"]["CSRE"]["CSREEnabled"]:
        if debug:
            print("[Core16] ALERT: Core System Recovery is enabled, preparing terminal")
        ogdata = fs.data
        fs.mkfile("P2", "/boot/env", "CSRE")
        in_csre = True
        print(f"[Core16] Project16 CSR Environment, version A10")
        print(f"[CSRE] To quit CSRE, type 'raise QuitCSRE'")
        log = []
        import sys, io
        while in_csre:
            try:
                try:
                    cmd = input("Core System> ")
                    log.append(f"[User] {cmd}")
                    if cmd == "revert()":
                        print("[CSRE] Reverting old FS")
                        log.append(f"[CSRE] Reverting old FS")
                        fs.data = ogdata
                        print("[CSRE] Old FS successfully reverted")
                        log.append(f"[CSRE] Old FS successfully reverted")
                    else:
                        exec(cmd)
                except QuitCSRE:
                    print("[CSRE] Exiting CSRE")
                    log.append("[CSRE] Exiting CSRE")
                    in_csre = False
            except Exception as e:
                print(f"[CSRE] Python: {type(e).__name__} ({e})")
                log.append(f"[CSRE] Python: {type(e).__name__} ({e})")
         
        if debug:
             print(f"[CSRE] Disabling CSRE")

        bootargs["Project16"]["CSRE"]["CSREEnabled"] = False
        bootargs["Project16"]["CSRE"]["CSRELastLog"] = log
        fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))
        if debug:
            print("[CSRE] CSRE disabled, exiting")
             
    else:
        if debug:
            print(f"[Core16] Preparing Project16")
        fs.mkfile("P2", "/boot/env", "Normal")
        fs.mkdir("P2", "/project")
            
        try:
            code = fs.catfile("P0", "/system/bin/shell")
            shell = types.ModuleType("shell")
            exec(code, shell.__dict__)
            api = Kernel(fs=fs)
            status = shell.init((bootargs, api, debug))
            if "/userlist" in fs.data["Partitions"]["P2"]["Tree"]:
                if debug:
                    print(f"[Core16] Userlist needs to be changed")
                fs.mkfile("P0", "/system/config/userlist", fs.catfile("P2", "/userlist"))
                if debug:
                    print(f"[Core16] Userlist updated")

            if status != None:
                if status[0] == "CSRE":
                    reason = status[1]
                    if debug:
                        print(f"[Core16] Project16 requested CSRE | Reason: {reason}")
                    bootargs["Project16"]["CSRE"]["CSREEnabled"] = True
                    fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))
        except Exception as e:
            if debug:
                print(f"[Core16] Unknown error while trying to load Project16: {type(e).__name__} ({e})")
                print(f"[Core16] Preparing next boot to CSRE mode")
            bootargs["Project16"]["CSRE"]["CSREEnabled"] = True
            fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))
            if debug:
                print(f"[Core16] Next boot set to CSRE")

            
    if debug:
        print("[Core16] Shutting down")
    fs.mkfile("P2", "/boot/power", "Off")
    return
