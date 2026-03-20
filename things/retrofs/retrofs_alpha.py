import uuid, json, time, os, base64

class RFSError(Exception):
    pass

class Filesystem:
    def _error(self, name, code, reason):
        print(f"RetroFS error: {code}")
        print(f"{name}: {reason}")
        raise RFSError(f"{name} ({code}): {reason}")
    
    def __init__(self, name="RetroFS"):
        self.data = {
            "Header": {
                "FSName": name,
                "FSCreation": time.time(),
                "FSUUID": str(uuid.uuid4())
            },
            "Partitions": {},
            "Size": {
                "Partitions": 0,
                "Folders": 0,
                "Files": 0,
                "Objects": 0
            }
        }
        
    def importfs(self, file):
        if not os.path.exists(file):
            self._error("ImportingError", "IMP_ERR01", f"Can't import FS from {file}: no such file or directory")
            
        self.data = json.loads(open(file, "r").read())
        
    def exportfs(self, file=None):
        if file == None:
            file = f"{self.data['Header']['FSName']}.rfs"
            
        open(file, "w").write(json.dumps(self.data, indent=4))
    
    def format(self, partid, partlabel):
        partition = {
            "PartitionLabel": partlabel,
            "PartitionUUID": str(uuid.uuid4()),
            "PartitionCreation": time.time(),
            "Tree": {
                "/": {
                    "ObjectType": "Folder",
                    "ObjectID": str(uuid.uuid4()),
                    "ObjectCreation": time.time(),
                    "ObjectProperties": ["ROOT", "IMMUTABLE"],
                    "ObjectData": None
                }
            }
        }
        if partid not in self.data["Partitions"]:
            self.data["Size"]["Partitions"] += 1
            
        self.data["Partitions"][partid] = partition
        self.data["Size"]["Folders"] += 1
        self.data["Size"]["Objects"] += 1
        
    def mkdir(self, partid, path):
        if partid not in self.data["Partitions"]:
            self._error("PartitionError", "PART_ERR01", "Can't create folder: partition not found")
            
        name = path
        path = path.split("/")[1:]
        cwd = "/"
        for dir in path:
            cwd += dir
            if cwd not in self.data["Partitions"][partid]["Tree"]:
                d = {
                    "ObjectType": "Folder",
                    "ObjectID": str(uuid.uuid4()),
                    "ObjectCreation": time.time(),
                    "ObjectProperties": [],
                    "ObjectData": None
                }
                self.data["Partitions"][partid]["Tree"][cwd] = d
                self.data["Size"]["Folders"] += 1
                self.data["Size"]["Objects"] += 1
            elif self.data["Partitions"][partid]["Tree"][cwd]["ObjectType"] != "Folder":
                self._error("RecursionError", "REC_ERR01", "Error while creating folder tree: can't continue recursion from a file")
                
            cwd += "/"
            
    def mkfile(self, partid, path, content):
        og = path
        path = path.split("/")[1:]
        filename = path[-1]
        path = path[:-1]
        path.insert(0, "")
        self.mkdir(partid, "/".join(path))
        f = {
            "ObjectType": "File",
            "ObjectID": str(uuid.uuid4()),
            "ObjectCreation": time.time(),
            "ObjectProperties": [],
            "ObjectData": base64.b64encode(content.encode()).decode()
        }
        self.data["Partitions"][partid]["Tree"][og] = f
        self.data["Size"]["Files"] += 1
        self.data["Size"]["Objects"] += 1
        
    def catfile(self, partid, path):
        if partid not in self.data["Partitions"]:
            self._error("PartitionError", "PART_ERR02", "Can't read file: partition not found")
            
        if path not in self.data["Partitions"][partid]["Tree"]:
            self._error("ReadError", "READ_ERR01", "Can't read file: no such file or directory")
            
        file = self.data["Partitions"][partid]["Tree"][path]
        if file["ObjectType"] != "File":
            self._error("ReadError", "READ_ERR02", "Can't read file: not a file")
            
        return base64.b64decode(file["ObjectData"].encode()).decode()
    
    def delete(self, partid, path):
        if partid not in self.data["Partitions"]:
            self._error("PartitionError", "PART_ERR03", "Can't delete object: partition not found")
            
        if path not in self.data["Partitions"][partid]["Tree"]:
            self._error("DeleteError", "DELETE_ERR01", "Can't delete object: no such file or directory")
            
        tree = self.data["Partitions"][partid]["Tree"]
        objs = []
        for obj in tree:
            objs.append(obj)
        
        for obj in objs:
            if obj.startswith(path):
                    del self.data["Partitions"][partid]["Tree"][obj]
        

