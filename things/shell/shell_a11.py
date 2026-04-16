def init(args):
    bootargs = args[0]
    api = args[1]
    debug = args[2]
    fs = api
    import json, time, types
    if debug:
        print(f"[Project16] Project16 loaded")
        
    print(f"Welcome to Project16!")
    if debug:
        print(f"[Project16] Starting login process")
        
    found = False
    userlist = json.loads(fs.catfile("P0", "/system/config/userlist")[1])
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
    if not fs.objectexists(userdata[1], userdata[0]):
        if debug:
            print(f"[Project16] Userdata is missing, unable to complete login")
        print(f"Error: can't finish login for {username}: missing userdata")
        if debug:
            print(f"[Project16] Exiting Project16")
        return ("CSRE", "Missing userdata")
    elif not fs.objectexists(appdata[1], appdata[0]):
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
            print(f"System version: Alpha 1.1")
            print(f"Kernel name: Core16")
            print(f"Kernel version: Alpha 1.1 - Standard Edition")
            
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
            
            code = fs.catfile(f"{folder}/main.pm", appdata[1])[1]
            if debug:
                print(f"[Project16] App code found, calling Platinum")
                
            platinum = types.ModuleType("platinum")
            pcode = fs.catfile("P1", "/bin/platinum")[1]
            exec(pcode, platinum.__dict__)
            if debug:
                print(f"[Project16] Platinum loaded on RAM, running app")
            
            mem = platinum.Memory(name="Project16's Platinum Memory")
            for line in code.splitlines():
                if debug:
                    print(f"[Platinum] Running line {repr(line)} in memory {mem.data['Header']['MemoryName']} (ID {mem.data['Header']['MemoryID']})")
                    
                platinum.LineParser(line, mem)
    return

