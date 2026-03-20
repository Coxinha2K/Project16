import time
class QuitCSRE(Exception):
    pass

def project16boot(args):
    bootargs = args[0]
    fs = args[1]
    debug = args[2]
    import json, time
    if debug:
        print(f"[Project16] Project16 loaded")
        
    print(f"Welcome to Project16!")
    if debug:
        print(f"[Project16] Starting login process")
        
    found = False
    userlist = json.loads(fs.catfile("P0", "/system/config/userlist"))
    while not found:
        username = input("Project16 username: ")
        if debug:
            print(f"[Project16] Got username {username}, looking up")
        if username not in userlist:
            found = False
            if debug:
                print(f"[Project16] {username} not found in userlist")
            print(f"Error: {username} not in userlist")
            continue
        else:
            found = True
            if debug:
                print(f"[Project16] User {username} found, logging in")
            continue
    
    print(f"Please wait, preparing {username} login...")
    userdata = bootargs["Project16"]["UserdataRoot"].split("@")
    appdata = bootargs["Project16"]["AppdataRoot"].split("@")
    userdata[0] += f"/{username}"
    appdata[0] += f"/{username}"
    if userdata[0] not in fs.data["Partitions"][userdata[1]]["Tree"]:
        if debug:
            print(f"[Project16] Userdata is missing, unable to complete login")
        print(f"Error: can't finish login for {username}: missing userdata")
        if debug:
            print(f"[Project16] Exiting Project16")
        return ("CSRE", "Missing userdata")
    elif appdata[0] not in fs.data["Partitions"][appdata[1]]["Tree"]:
        if debug:
            print(f"[Project16] Appdata is missing, unable to complete login")
        print(f"Error: can't finish login for {username}: missing appdata")
        if debug:
            print(f"[Project16] Exiting Project16")
        return ("CSRE", "Missing appdata")
    user = userlist[username]
    if user["LastLogged"] == None:
        if debug:
            print(f"[Project16] This is {username}'s first login")
        userlist[username]["LastLogged"] = time.time()
        print(f"Welcome to Project16, {username}! We hope you like it!")
    else:
        if debug:
            print(f"[Project16] {username}'s last login is {user['LastLogged']}")
        userlist[username]["LastLogged"] = time.time()
        print(f"Welcome back to Project16, {username}!")
        
    if debug:
        print(f"[Project16] Changing userlist")
    fs.mkfile("P2", "/userlist", json.dumps(userlist))
    if debug:
        print(f"[Project16] Preparing user")
        

    running = True
    if "ROOT" in user["Properties"]:
        prompt = f"{username}@project16 # "
    else:
        prompt = f"{username}@project16 $ "
    if debug:
        print(f"[Project16] User prepared, opening terminal")
        
    while running:
        cmd = input(prompt)
        if debug:
            print(f"[Project16] Got command {repr(cmd)}")
        if cmd.lower() in ("exit", "quit"):
            running = False
            if debug:
                print(f"[Project16] Exiting Project16")
            continue
        elif cmd.lower() == "csre":
            if "ROOT" not in user["Properties"]:
                if debug:
                    print(f"[Project16] CSRE access denied for {username}")
                print("Error: not a root user to boot CSRE")
            else:
                if debug:
                    print(f"[Project16] CSRE access requested by {username}, checking...")
                if "OWNER" in user["Properties"]:
                    print(f"Hello {username} (Install Owner)! Rebooting to CSRE...")
                    if debug:
                        print(f"[Project16] {username} is the install owner, rebooting now")
                    return ("CSRE", "Install Owner request")
                else:
                    if debug:
                        print(f"[Project16] Checking access for {username}")
                if input("Type your username: ") != username:
                    if debug:
                        print("[Project16] CSRE access denied")
                    print("Error: access denied")
                else:
                    if debug:
                        print(f"[Project16] CSRE access granted for {username}, rebooting")
                    print("Rebooting to CSRE...")
                    return ("CSRE", "Root user request")
                
        elif cmd == "info":
            print(f"System name: Project16")
            print(f"System version: Alpha 1.0")
            print(f"Kernel name: Core16")
            print(f"Kernel version: Alpha 1.0 - Standard Edition")
            
        else:
            try:
                fs.data["Partitions"][appdata[1]]["Tree"][f"{appdata[0]}/{cmd}"]
                folder = f"{appdata[0]}/{cmd}"
                if debug:
                    print(f"[Project16] Found app {cmd}, trying to run it")
            except:
                print(f"Project16: No such command {cmd}")
                if debug:
                    print(f"[Project16] {cmd} is not a command")
                continue
            
            code = fs.catfile(f"{folder}/main.pm", appdata[1])
            if debug:
                print(f"[Project16] App code found, calling Platinum")
                
            
    return

def core16boot(args):
    bootargs = args[0]
    fs = args[1]
    debug = bootargs["Core16"]["Debug"]
    if debug:
        print("[Core16] Project16 Core16 SE, version A10")
        print("[Core16] Loading filesystem")
    import json
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
            status = project16boot((bootargs, fs, debug))
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
