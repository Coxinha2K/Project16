import time, json, requests, types
print("Project16 Installer")
username = input("[?] Username for Project16: ")
print("[i] Starting install process...")
base = "https://raw.githubusercontent.com/Coxinha2K/Project16/main"
print("[i] Downloading RetroFS...")
rfs_code = requests.get(f"{base}/things/retrofs/retrofs_alpha.py").text
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
core16 = requests.get(f"{base}/things/core16/core16_a10_se.py").text

fs.mkdir("P0", "/system")
fs.mkdir("P0", "/system/config")
fs.mkfile("P0", "/system/core.16", core16)

print("[i] Install step 4 - creating userdata")
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

print("[i] Install step 5 - installing Platinum")
platinum_code = requests.get(f"{base}/things/platinum/platinum_a10.py").text
fs.mkfile("P1", "/bin/platinum", platinum_code)

print("[i] Install step 6 - adding final touches")
systemver = {
    "OSName": "Project16",
    "OSVersion": "A10",
    "OSFullName": "Project16 Alpha 1.0",
    "OSInstallDate": int(time.time()),
    "OSOwner": username
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

print("[i] Install step 7 - exporting FS")
fs.exportfs(file=f"Project16.rfs")

print("[i] Project16 installation finished!")
