import uuid, sys, random

def error(name, code, reason, a=None):
    print(f"Platinum Error: {code}")
    print(f"{name}: {reason}")
    if a != None:
        print(f"Details: {a}")
        
    sys.exit()

class Memory:
    def __init__(self, name="Platinum Standard Memory"):
        self.data = {
            "Header": {
                "MemoryName": name,
                "MemoryID": str(uuid.uuid4())
            },
            "Memory": {
                "Variables": {},
                "Functions": {}
            }
        }
        
    def addvar(self, name, value):
        if name in self.data["Memory"]["Variables"]:
            error("MemoryError", "TPP_MEMORY-001", f"Variable {name} already exists", a=f"Memory: {self.data['Header']['MemoryName']} (ID {self.data['Header']['MemoryID']})")
            
        self.data["Memory"]["Variables"][name] = value
        
    def getvar(self, name):
        if name not in self.data["Memory"]["Variables"]:
            error("MemoryError", "TPP_MEMORY-002", f"Variable {name} not found", a=f"Memory: {self.data['Header']['MemoryName']} (ID {self.data['Header']['MemoryID']})")
            
        return self.data["Memory"]["Variables"][name]
    
    def delvar(self, name):
        if name not in self.data["Memory"]["Variables"]:
            error("MemoryError", "TPP_MEMORY-002", f"Variable {name} not found", a=f"Memory: {self.data['Header']['MemoryName']} (ID {self.data['Header']['MemoryID']})")
            
        del self.data["Memory"]["Variables"][name]
        
    def modvar(self, name, newvalue):
        if name not in self.data["Memory"]["Variables"]:
            error("MemoryError", "TPP_MEMORY-002", f"Variable {name} not found", a=f"Memory: {self.data['Header']['MemoryName']} (ID {self.data['Header']['MemoryID']})")
            
        self.data["Memory"]["Variables"][name] = newvalue
        
def TextNormalizer(text, memory, finalspace=False):
    final = ""
    if text.startswith("'") and text.endswith("'"):
        text = text[1:][:len(text) - 2]
        for word in text.split():
            if word.startswith("%") and word.endswith("%"):
                word = word[1:][:len(word) - 2]
                final += memory.getvar(word)
            else:
                final += word
                
            final += " "
    else:
        final = memory.getvar(text)
        
    if final.endswith(" "):
        if finalspace:
            final += " "*1
        return final[:-1]
    else:
        if finalspace:
            final += " "*1
        return final

def LineParser(line, memory):
    line = line.split()
    try:
        cmd = line[0]
        args = line[1:]
    except IndexError:
        return
    
    if cmd == "Print":
        text = " ".join(args)
        final = TextNormalizer(text, memory)
        print(final)
       
    elif cmd == "Set":
        name = args[0]
        value = " ".join(args[1:])
        value = TextNormalizer(value, memory)
        if name in memory.data["Memory"]["Variables"]:
            memory.modvar(name, value)
        else:
            memory.addvar(name, value)
                
    elif cmd == "Input":
        var = args[0]
        prompt = TextNormalizer(" ".join(args[1:]), memory, finalspace=True)
        value = input(prompt)
        if var in memory.data["Memory"]["Variables"]:
            memory.modvar(var, value)
        else:
            memory.addvar(var, value)
        
    elif cmd == "Version":
        print("The Platinum Project, version 1.0 alpha (MR12)")
        
    elif cmd == "Exit" or cmd == "Stop":
        sys.exit()
    
    elif cmd.startswith("#"):
        pass
    
    else:
        error("SyntaxError", "TPP_SYNTAX-001", f"Syntax error: {cmd} not found")
        
def FileParser(file):
    memory = Memory()
    try:
        code = open(file, "r").read()
    except Exception as e:
        error("ParsingError", "TPP_PARSER-001", f"Couldn't parse file {file}: read error ({type(e).__name__}: {e})")
        
    for line in code.splitlines():
        LineParser(line, memory)

if __name__ == "__main__":
    try:
        file = sys.argv[1]
        FileParser(file)
    except Exception as e:
        print("The Platinum Project, version 1.0 alpha")
        repl_memory = Memory(name="Platinum REPL Memory")
        while True:
            cmd = input("repl@platinum $ ")
            if cmd == "ReplReason":
                print(f"REPL reason: exception {type(e).__name__} ({e})")
            elif cmd == "ReplRaise":
                error(type(e).__name__, "TPP_REPL-001", e)
            elif cmd == "ReplVersion":
                print("The Platinum Project, REPL version 1.0 alpha")
            else:
                LineParser(cmd, repl_memory)

