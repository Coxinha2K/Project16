import time, hashlib, socket, json, types
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
        self.protected = {}
        if self.debug:
            print(f"[Core16 API] Waiting API (authority) configuration")
            
        """
        Authority system for Core16:
        Permissions is a list of strings that define what the authority can do
        FS_ACCESS: This permission lets the authority use the FS directly, meaning that the authority can access the FS object entirely, bypassing the standard FS API (mkdir, mkfile, etc)
        FS_READ: This permission lets the authority read the FS using the standard FS API (mkdir, mkfile, all this sh*t)
        FS_WRITE: This permission lets the authority write to the FS using the standard FS API (mkdir, mkfile, i don't want to repeat ts again)
        CONFIG_READ: This permission lets the authority read the configs (boot.cfg and system.ini)
        RESTRICTED_ACCESS: This permission lets the authority write in places that Core16 protects, e.g Partition 0 (P0 - Boot)
        API_CALLS: This permission lets the authority call the Kernel API for using the actual functions, like the entire FS API
        BETA_GUI: This permission enables the Beta 1.0 GUI feature
        GUI_CONTROL: This permission lets the authority control the GUI (enable/disable service, start/stop the server)
        GUI_TOOL: This permission enables the toolset available for the GUI feature
        Back to the authority thing, this is not persistent!
        This is not saved anywhere, like:
        - the VRAM (virtual RAM, not video RAM) don't store it
        - it don't go to RetroFS
        - and it stays on the real RAM, but gets lost when you kill the system
        """
       
    class GUI:
        def __init__(self, authority, name="Core16 Beta GUI", debug=False):
            self.name = name
            self.authority = authority
            self.debug = debug
            self.settings = {
                "GUIEnabled": False,
                "GUIControllingEnabled": False,
                "GUIToolboxEnabled": False,
                "GUIServerName": self.name,
                "GUIServerPort": 5200,
                "GUIPassword": {
                    "PasswordEnabled": False,
                    "PasswordValue": None
                }
            }
            if self.debug:
                print(f"[Beta GUI] GUI object created, name: {self.name}")
                
        def setup(self, mode="auto", data={}):
            if self.debug:
                print(f"[Beta GUI] Setting up GUI - {mode} setup")
                
            if mode == "auto":
                settings = {
                    "GUIEnabled": False,
                    "GUIControllingEnabled": False,
                    "GUIToolboxEnabled": False,
                    "GUIServerName": self.name,
                    "GUIServerPort": 5200,
                    "GUIPassword": {
                        "PasswordEnabled": False,
                        "PasswordValue": None
                    }
                }
                if "BETA_GUI" not in self.authority.authority["Data"]["Permissions"]:
                    if self.debug:
                        print(f"[Beta GUI] BETA_GUI permission not found")
                        print(f"[Beta GUI] Note: there is no BETA_GUI here so the setup won't be able to check GUI_CONTROL and GUI_TOOL, sorry :(")
                    settings["GUIEnabled"] = False
                else:
                    settings["GUIEnabled"] = True
                    if self.debug:
                        print(f"[Beta GUI] Note: GUI controlling and GUI toolbox can only be enabled/disabled automatically if BETA_GUI is in permissions (like right now)")
                    if "GUI_CONTROL" not in self.authority.authority["Data"]["Permissions"]:
                        if self.debug:
                            print(f"[Beta GUI] GUI_CONTROL permission not found")
                        settings["GUIControllingEnabled"] = False
                    else:
                        settings["GUIControllingEnabled"] = True
                        
                    if "GUI_TOOL" not in self.authority.authority["Data"]["Permissions"]:
                        if self.debug:
                            print(f"[Beta GUI] GUI_TOOL permission not found")
                        settings["GUIToolboxEnabled"] = False
                    else:
                        settings["GUIToolboxEnabled"] = True
                if self.debug:
                    print(f"[Beta GUI] Automatic setup finished, applying")
                self.settings = settings
                if self.debug:
                    print(f"[Beta GUI] Settings applied!")
                    
            elif mode == "manual":
                if data == {}:
                    if self.debug:
                        print(f"[Beta GUI] Tried manual setup but there is nothing in the new settings, starting automatic setup")
                    self.setup(mode="auto")
                else:
                    self.settings = data
                    if self.debug:
                        print(f"[Beta GUI] Settings applied!")
            else:
                if self.debug:
                    print(f"[Beta GUI] Unknown setup mode, using automatic setup")
                self.setup(mode="auto")
                        
    def read_fs(self):
        if self.authority["Configured"]:
            if "API_CALLS" not in self.authority["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't read FS: WHY API_CALLS ISN'T IN PERMISSION THAT DOESN'T MAKE SENSE WTH")
                    
                return (1, "API calls not allowed")
            if self.debug:
                print(f"[Core16 API] {self.authority['Data']['Name']} is the current authority")
            if "FS_RAW_READ" in self.authority["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Access granted to FS, returning it")
                return (0, self.fs)
            else:
                if self.debug:
                    print(f"[Core16 API] Can't read since there is no permission to read FS")
                return (1, "No permission to read FS")
        else:
            if self.debug:
                print(f"[Core16 API] Can't read FS since authority is not configured")
                
    def _disabledsetup(self, name=None, permissions=None):
        if self.debug:
            print(f"[Core16 API] Tried to run authority setup but it's disabled")
            
    def authority_setup(self, name="Core16 Authority for Project16", permissions=None, protected=None):
        if permissions == None:
            if self.debug:
                print(f"[Core16 API] No permissions configured, using standard")
                
            permissions = ["FS_READ", "FS_WRITE", "API_CALLS", "CONFIG_READ"]
            
        if protected == None:
            if self.debug:
                print(f"[Core16 API] No protected partitions configured, using standard")
            
            protected = {
                "P0": "Critical partition to system operation"
            }
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
        self.protected = protected
        if self.debug:
            print(f"[Core16 API] Current authority to this API: {name} | Permissions: {permissions}")
            print(f"[Core16 API] Disabling authority setup")
            
        try:
            self.authority_setup = self._disabledsetup
        except AttributeError:
            pass
        
    def mkdir(self, partition, path):
        if self.debug:
            print(f"[Core16 API] Creating folder {path}@{partition}")
            
        a = self.authority
        if a["Configured"]:
            if "API_CALLS" not in a["Data"]["Permissions"]:
                if self.debug:
                    print(f"[Core16 API] Can't create folder... no API_CALLS... wth this dont make any sense why we can call the kernel btw")
                return (1, "No API calls allowed")
            
            if partition in self.protected:
                if "RESTRICTED_ACCESS" not in a["Data"]["Permissions"]:
                    if self.debug:
                        print(f"[Core16 API] Can't operate: tried write to FS partition {partition} but it is protected ({self.protected[partition]})")
                    return
                
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

            if partition in self.protected:
                if "RESTRICTED_ACCESS" not in a["Data"]["Permissions"]:
                    if self.debug:
                        print(f"[Core16 API] Can't operate: tried write to FS partition {partition} but it is protected ({self.protected[partition]})")
                    return
                
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
                return (1, "Can't read file from filesystem")
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
                    
    def bootcfg(self):
        if self.debug:
            print(f"[Core16 API] Trying to read boot.cfg (/system/config/boot.cfg@P0)")
        
        if self.authority["Configured"]:
            if "API_CALLS" in self.authority["Data"]["Permissions"]:
                if "CONFIG_READ" in self.authority["Data"]["Permissions"]:
                    if self.debug:
                        print(f"[Core16 API] Calling self.catfile to read boot.cfg")
                    boot = self.catfile("P0", "/system/config/boot.cfg")[1]
                    if self.debug:
                        print(f"[Core16 API] Got boot.cfg, returning in JSON")
                    return json.loads(boot)
                else:
                    if self.debug:
                        print(f"[Core16 API] Couldn't read boot.cfg: CONFIG_READ not found")
                    return {}
            else:
                if self.debug:
                    print(f"[Core16 API] Couldn't read boot.cfg: API_CALLS not found")
                return {}
        else:
            if self.debug:
                print(f"[Core16 API] Couldn't read boot.cfg: authority not configured")
            return {}

    def systemini(self):
        if self.debug:
            print(f"[Core16 API] Trying to read system.ini (/system/config/system.ini@P0)")
        
        if self.authority["Configured"]:
            if "API_CALLS" in self.authority["Data"]["Permissions"]:
                if "CONFIG_READ" in self.authority["Data"]["Permissions"]:
                    if self.debug:
                        print(f"[Core16 API] Calling self.catfile to read system.ini")
                    sys = self.catfile("P0", "/system/config/system.ini")[1]
                    if self.debug:
                        print(f"[Core16 API] Got system.ini, returning in JSON")

                    return json.loads(sys)
                else:
                    if self.debug:
                        print(f"[Core16 API] Couldn't read system.ini: CONFIG_READ not found")
                    return {}
            else:
                if self.debug:
                    print(f"[Core16 API] Couldn't read system.ini: API_CALLS not found")
                return {}
        else:
            if self.debug:
                print(f"[Core16 API] Couldn't read system.ini: authority not configured")
            return {}
        
def core16boot(args):
    bootargs = args[0]
    fs = args[1]
    debug = bootargs["Core16"]["Debug"]
    if debug:
        print(f"[Core16] Project16 Core16 SE, version B10")
        print(f"[Core16] Loading filesystem")

    if debug:
        print(f"[Core16] Preparing VRAM...")
    if bootargs["ResetVRAM"]:
        fs.format("P2", "RAM")
    else:
        if debug:
            print(f"[Core16] Note: ResetVRAM=False, unable to reset VRAM")
    
    fs.mkfile("P2", "/boot/power", "On")
    if bootargs["Project16"]["CSRE"]["CSREEnabled"]:
        if debug:
            print(f"[Core16] ALERT: Core System Recovery is enabled, preparing terminal")
        ogdata = fs.data
        fs.mkfile("P2", "/boot/env", "CSRE")
        in_csre = True
        print(f"[Core16] Project16 CSR Environment, version A10")
        print(f"[CSRE] To quit CSRE, type 'raise QuitCSRE'")
        log = []

        while in_csre:
            try:
                try:
                    cmd = input("Core System> ")
                    log.append(f"[User] {cmd}")
                    if cmd == "revert()":
                        print(f"[CSRE] Reverting old FS")
                        log.append(f"[CSRE] Reverting old FS")
                        fs.data = ogdata
                        print(f"[CSRE] Old FS successfully reverted")
                        log.append(f"[CSRE] Old FS successfully reverted")
                    else:
                        exec(cmd)
                except QuitCSRE:
                    print(f"[CSRE] Exiting CSRE")
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
            print(f"[CSRE] CSRE disabled, exiting")
             
    else:
        if debug:
            print(f"[Core16] Preparing Project16")
        fs.mkfile("P2", "/boot/env", "Normal")
        fs.mkdir("P2", "/project")
            
        try:
            shell_path = json.loads(fs.catfile("P0", "/system/config/system.ini"))["Shell"].split("@")
            code = fs.catfile(shell_path[1], shell_path[0])
            shell = types.ModuleType("shell")
            exec(code, shell.__dict__)
            api = Kernel(bootargs, fs, debug=debug)
            api.authority_setup()
            snapshots = {}
            for partition in api.protected:
                if debug:
                    print(f"[Core16] Snapshoting partition {partition}")
                snapshots[partition] = json.dumps(fs.data["Partitions"][partition])
                if debug:
                    print(f"[Core16] Partition {partition} snapshoted")
            
            if debug:
                print(f"[Core16] Ready to boot Project16")
                
            status = shell.init((bootargs, api, debug))
            if debug:
                print(f"[Core16] Project16 offline, verifying protected partitions")
                
            for partition in api.protected:
                if debug:
                    print(f"[Core16] Verifying partition {partition}")
                snapshot_og = snapshots[partition]
                snapshot_now = json.dumps(fs.data["Partitions"][partition])
                og = hashlib.sha256(snapshot_og.encode()).hexdigest()
                now = hashlib.sha256(snapshot_now.encode()).hexdigest()
                if og != now:
                    if debug:
                        print(f"[Core16] Verification failed, reverting to previous snapshot of {partition}")
                    fs.data["Partitions"][partition] = json.loads(snapshot_og)
                    if debug:
                        print(f"[Core16] Snapshot reverted")
                else:
                    if debug:
                        print(f"[Core16] Verification successfull, no tampering detected on partition {partition}")
                        
                if debug:
                    print(f"Original snapshot of {partition} (SHA256): {og}")
                    print(f"Current snapshot of {partition} (SHA256): {now}")
                    
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
        print(f"[Core16] Shutting down")
    fs.mkfile("P2", "/boot/power", "Off")
    return

