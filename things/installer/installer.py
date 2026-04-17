import time, json, requests, types
print("Project16 Installer")
username = input("[?] Username for Project16: ")
print("[i] Starting install process...")
base = "https://raw.githubusercontent.com/Coxinha2K/Project16/main"
print("[i] Downloading version list...")
vlist = json.loads(requests.get(f"{base}/versions.json").text)
print("[i] Downloading RetroFS...")
rfs_code = requests.get(f"{base}/{vlist['RetroFS']['Latest']['Path']}").text
print("[i] Loading RetroFS...")
name = "rfs"
rfs = types.ModuleType(name)
exec(rfs_code, rfs.__dict__)
print("[i] Install step 1 - creating filesystem")
fs = rfs.Filesystem(name="Project16")

print("[i] Install step 2 - formatting partitions")
fs.format("P0", "Boot")
fs.format("P1", "Project16")
fs.format("P2", "RAM")

print("[i] Install step 3 - installing Core16")
core16 = requests.get(f"{base}/{vlist['Core16']['Latest']['Path']}").text
# core16 = open("stuff/core16.py", "r").read()
fs.mkdir("P0", "/system")
fs.mkdir("P0", "/system/config")
fs.mkfile("P0", "/system/core.16", core16)

print("[i] Install step 4 - installing Project16 shell")
shell = requests.get(f"{base}/{vlist['Shell']['Latest']['Path']}").text
# shell = open("shell.py", "r").read()
fs.mkdir("P0", "/system/bin")
fs.mkfile("P0", "/system/bin/shell", shell)

print("[i] Install step 5 - creating userdata")
fs.mkdir("P1", f"/users/{username}")
fs.mkdir("P1", f"/appdata/{username}")
fs.mkdir("P1", "/bin")
userlist = {
    username: {
        "CreatedAt": time.time(),
        "LastLogged": None,
        "Level": "Owner",
        "Properties": ["OWNER", "ROOT"]
    }
}
fs.mkfile("P0", "/system/config/userlist", json.dumps(userlist))

print("[i] Install step 6 - installing Platinum")
platinum_code = requests.get(f"{base}/{vlist['Platinum']['Latest']['Path']}").text
fs.mkfile("P1", "/bin/platinum", platinum_code)

print("[i] Install step 7 - adding final touches")
fs.mkdir("P0", "/system/bin")
systemver = {
    "OSName": "Project16",
    "OSVersion": f"{vlist['Shell']['Latest']['Version']}",
    "OSInstallDate": int(time.time()),
    "OSOwner": username,
    "Shell": "/system/bin/shell@P0"
}
fs.mkfile("P0", "/system/config/system.ini", json.dumps(systemver))
bootargs = {
    "Core16": {
        "Version": "A10",
        "Edition": "SE",
        "Path": "/system/core.16@P0",
        "Debug": False
    },
    "Project16": {
        "SystemInfo": "/system/config/system.ini@P0",
        "UserdataRoot": "/users@P1",
        "AppdataRoot": "/appdata@P1",
        "CSRE": {
            "CSREEnabled": False,
            "CSRELastLog": []
        }
    },
    "ResetVRAM": True
}
fs.mkfile("P0", "/system/config/boot.cfg", json.dumps(bootargs))

print("[i] Install step 8 - exporting FS")
fs.exportfs(file=f"Project16.rfs")

print("[i] Project16 installation finished!")
