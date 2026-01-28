import smbus # pyright: ignore[reportMissingImports] # Like... I don't have this on my Mac...
import struct
import socket
import os
import threading

# Configs

I2CBus = 1 # Your I2C bus
I2CAddress = 0x36 # Your I2C device address
ListeningAddress = "" # Doesn't really matter innit? At least for a service behind NAT.
ListeningPort = 8101 # Port you wanna to use
HTMLPath = "dash.html" # Whatever HTML you want to use, be aware of those variables

# Initialize payloads
def InitializePayload() -> tuple:
    assets = {"voltage": 0.0000, "capacity": 0.0000, "temp": "",
           "time": "", "uptime": "", "upsince": "", "header": "", "load": ""}
    VisitCount = 0
    LastUA = ""
    IPLast = ""
    return assets, VisitCount, LastUA, IPLast

def HTMLRead() -> str:
    try:
        with open(HTMLPath, 'r') as file:
            HTMLData = file.read()
    except FileNotFoundError:
        print(f"{HTMLPath} was not found.")
        raise SystemExit
    except PermissionError:
        print(f"You sure you can read this file? Check file permission of {HTMLPath}")
        raise SystemExit
    return HTMLData

def I2CRead(bus, i2caddr, addr) -> int:
    try:
        tmp = bus.read_word_data(i2caddr, addr)
    except SystemError:
        raise SystemError
    tmp = struct.unpack("<H", struct.pack(">H", tmp))[0]
    return tmp
    
def BatteryPackVoltage(bus) -> float:
    I2CReading = I2CRead(bus, I2CAddress, 2)
    voltage = I2CReading*1.25/1000/16
    return voltage

def BatteryPackCapacity(bus) -> float:
    I2CReading = I2CRead(bus, I2CAddress, 4)
    capacity = I2CReading/256
    return capacity

def SimpHTTPServerSetup():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((ListeningAddress, ListeningPort))
        s.listen(4)
    except socket.error:
        raise SystemError
    return s

def SimpHeaderRead(Data: bytes) -> dict:
    ProDict = {"Origin": "", "CfIP": "", "CfCountry": "", "CfRayID": "", "UA": ""}
    DecodedData = Data.decode()
    for key in DecodedData.split("\r\n"):
        RawList = key.split("\r\n")
        if len(RawList[0].split(": ")) > 1:
            Value = RawList[0].split(": ")[1]
            Key = RawList[0].split(": ")[0]
            match Key:
                case "Cf-Connecting-Ip":
                    ProDict["Origin"] = Value
                case "X-Forwarded-For":
                    ProDict["CfIP"] = Value
                case "Cf-Ipcountry":
                    ProDict["CfCountry"] = Value
                case "Cf-Ray":
                    ProDict["CfRayID"] = Value
                case "User-Agent":
                    ProDict["UA"] = Value
        else:
            pass
    return ProDict

def SimpHTTPSend(client, address, assets, VisitCount, LastUA, IPLast):
    IncomingData = client.recv(1024)
    ProDict = SimpHeaderRead(IncomingData)
    if ProDict["UA"] != LastUA and ProDict["Origin"] != IPLast and ProDict["Origin"] != "":
        VisitCount = VisitCount + 1
        print("Unique.")
        print(f"{ProDict['Origin']} comp {IPLast}")
    print(f"Incoming traffic from {ProDict['Origin']} via {address[0]}:{address[1]}")
    Response = HTMLRead()
    try:
        Response = Response.format(
        LoadAvg = assets["load"], RealAddr = ProDict["Origin"], CfCDNIP = ProDict["CfIP"], CfCDNLOC = ProDict["CfCountry"], 
        addr = address[0], port = address[1], volt = assets["voltage"], percent = assets["capacity"], temps = assets["temp"], 
        timenow = assets["time"], uptime = assets["uptime"], upsince = assets["upsince"], header = IncomingData.decode(), visit = VisitCount
        )
    except KeyError:
        pass
    try:
        client.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        client.send(bytes(Response.encode("utf-8")))
    except socket.timeout or BrokenPipeError or ConnectionAbortedError as error:
        print(f"{error} when sending to {address[0]}:{address[1]}, skipped.")
    IPLast = ProDict["Origin"]
    return VisitCount, LastUA, IPLast
    

def VCTempRead() -> str:
    VCTemp = os.popen("vcgencmd measure_temp").read().split("=")[1].split("\n")[0]
    return VCTemp

def TimeRelated() -> tuple[str, str, str, str]:
    LoadAverage = os.popen("uptime").read().split("\n")[0].split(",  ")[-1].split(": ")[-1]
    UPTimeSince = os.popen("uptime -s").read().split("\n")[0]
    UPTimeFor = os.popen("uptime -p").read().split("\n")[0][3:]
    LocalTimeTup = os.popen("date").read().split("\n")[0].split(" ")
    LocalTime = f"{LocalTimeTup[0]} {LocalTimeTup[1]}, {LocalTimeTup[2]} {LocalTimeTup[5]} {LocalTimeTup[3]} (UTC{LocalTimeTup[4]})"
    return UPTimeSince, UPTimeFor, LocalTime, LoadAverage

def HardReadingOperations(bus) -> dict:
    assets["voltage"] = BatteryPackVoltage(bus)
    assets["capacity"] = BatteryPackCapacity(bus)
    assets["temp"] = VCTempRead()
    assets["upsince"], assets["uptime"], assets["time"], assets["load"] = TimeRelated()
    return assets

def ServerStage(client, address, assets, bus, VisitCount, LastUA, IPLast):
    assets = HardReadingOperations(bus)
    VisitCount, LastUA, IPLast = SimpHTTPSend(client, address, assets, VisitCount, LastUA, IPLast)
    client.close()
    return VisitCount, LastUA, IPLast

def main(assets, VisitCount, LastUA, IPLast):
    bus = smbus.SMBus(I2CBus)
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ListeningAddress, ListeningPort))
    except socket.error:
        raise SystemError
    while True:
        try:
            s.listen(4)
            # OMG IDK BUT THIS SHOULD BE WHERE MULTI THREADING BEGINS.
            # I don't think I need that now? Or does I understand the needs of "Multi-threading" badly.
            # Maybe I don't need that anyway, just let s.listen(4) which enable 4 additional connections to wait till actually got accepted?
            # Shit.
            client, address = s.accept()
            VisitCount, LastUA, IPLast = ServerStage(client, address, assets, bus, VisitCount, LastUA, IPLast)
            
            client.close()
        except BrokenPipeError:
            client.close()
            print(f"Broken pipe to {IPLast} via {address}.")
            pass
        except OSError as error:
            client.close()
            raise error
        except KeyboardInterrupt:
            client.close()
            print("Interrupt by user.")
            break

if __name__ == "__main__":
    assets, VisitCount, LastUA, IPLast = InitializePayload()
    main(assets, VisitCount, LastUA, IPLast)

