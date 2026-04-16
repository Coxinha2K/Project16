import time
class QuitCSRE(Exception):
    pass

class Kernel:
    def __init__(self, bootargs, fs, debug=False):
        self.authority = {
            "Configured": False,
            "Data": {
                "Name": None,
                "Permissions": []
            }
        }
        self.fs = fs
        self.debug = debug
        if self.debug:
            print("[Core16 API] Waiting API (authority) configuration")
            
        """
        Authority system for Core16:
        Permissions is a list of strings that define what the authority can do
        FS_ACCESS: This permission lets the authority use the FS directly, meaning that the authority can access the FS object entirely, bypassing the standard FS API (mkdir, mkfile, etc)
        FS_READ: This permission lets the authority read the FS using the standard FS API (mkdir, mkfile, all this sh*t)
        FS_WRITE: This permission lets the authority write to the FS using the standard FS API (mkdir, mkfile, i don't want to repeat ts again)
        API_CALLS: This permission lets the authority call the Kernel API for using the actual functions, like the entire FS API
        Back to the authority thing, this is not persistent!
        This is not saved anywhere, like:
        - the VRAM (virtual RAM, not video RAM) don't store it
        - it don't go to RetroFS
        - and it stays on the real RAM, but gets lost when you kill the script
        """
        
    def read_fs(self):
        if self.authority["Configured"]:
            if "API_CALLS" not in self.authority["Data"]["Permissions"]:
                if self.debug:
                    print("[Core16 API] Can't read FS: WHY API_CALLS ISN'T IN PERMISSION THAT DOESN'T MAKE SENSE WTH")
                    
                return (1, "API calls not allowed")
            if self.debug:
                print(f"[Core16 API] {self.authority['Data']['Name']} is the current authority")
            if "FS_RAW_READ" in self.authority["Data"]["Permissions"]:
                if self.debug:
                    print("[Core16 API] Access granted to FS, returning it")
                return (0, self.fs)
            else:
                if self.debug:
                    print("[Core16 API] Can't read since there is no permission to read FS")
                return (1, "No permission to read FS")
        else:
            if self.debug:
                print("[Core16 API] Can't read FS since authority is not configured")
                
    def _disabledsetup(self, name=None, permissions=None):
        if self.debug:
            print("[Core16 API] Tried to run authority setup but it's disabled")
            
    def authority_setup(self, name="Core16 Authority for Project16", permissions=None):
        if permissions == None:
            if self.debug:
                print("[Core16 API] No permissions configured, using standard")
                
            permissions = ["FS_READ", "FS_WRITE", "API_CALLS"]
            
        authority = {
            "Configured": True,
            "Data": {
                "Name": name,
                "Permissions": permissions
            }
        }
        if self.debug:
            print(f"[Core16 API] Configuring {name}'s authority")
            
        self.authority = authority
        if self.debug:
            print(f"[Core16 API] Current authority to this API: {name} (level {level}) | Permissions: {permissions}")
            print("[Core16 API] Disabling authority setup")
            
        self.authority_setup = self._disabledsetup
            
    def mkdir(self, partition, path):
        if self.debug:
            print(f"[Core16 API] Creating folder {path}@{partition}")
            
        a = self.authority
        if a["Configured"]:
            if "API_CALLS" not in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't create folder... no API_CALLS... wth this dont make any sense why we can call the kernel btw")
                return (1, "No API calls allowed")
            
            if "FS_WRITE" in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Creating folder (permissions check out)")
                self.fs.mkdir(partition, path)
            else:
                if self.debug:
                    print(f"[Core16 API] Can't create folder: can't write to filesystem")
                    
    def mkfile(self, partition, path, content):
        if self.debug:
            print(f"[Core16 API] Creating file {path}@{partition}")
            
        a = self.authority
        if a["Configured"]:
            if "API_CALLS" not in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't create file... no API_CALLS... wth this dont make any sense why we can call the kernel btw")
                return (1, "No API calls allowed")

            if "FS_WRITE" in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Creating file (permissions check out)")
                self.fs.mkfile(partition, path, content)
            else:
                if self.debug:
                    print(f"[Core16 API] Can't create file: can't write to filesystem")
                    
    def catfile(self, partition, path):
        if self.debug:
            print(f"[Core16 API] Reading file {path}@{partition}")
            
        a = self.authority
        if a["Configured"]:
            if "API_CALLS" not in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't read file... no API_CALLS... wth this dont make any sense why we can call the kernel btw")
                return (1, "No API calls allowed")
        
            if "FS_READ" in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Reading file (permissions check out)")
                return (0, self.fs.catfile(partition, path))
            else:
                if self.debug:
                    print(f"[Core16 API] Can't read file: can't read from filesystem")
                
    def objectexists(self, partition, path):
        if self.debug:
            print(f"[Core16 API] Verifying if {path}@{partition} exists")
            
        a = self.authority
        if a["Configured"]:
            if "API_CALLS" not in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't verify... no API_CALLS... wth this dont make any sense why we can call the kernel btw")
                return (1, "No API calls allowed")
            
            if "FS_READ" in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Verifying (permissions check out)")
                if path not in self.fs.data["Partitions"][partition]["Tree"]:
                    return False
                else:
                    return True
                
            else:
                if self.debug:
                    print(f"[Core16 API] Can't verify: can't read from filesystem")
                    
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
            api = Kernel(bootargs, fs, debug=debug)
            api.authority_setup()
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
