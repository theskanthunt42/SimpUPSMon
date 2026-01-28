import smbus
import struct
import socket
import os

I2CBus = 1
I2CAddress = 0x36 
ListeningAddress = "" #Doesn't really matter innit? At least for a service behind NAT.
ListeningPort = 8101

VisitCount = 0

assets = {"voltage": 0.0000, "capacity": 0.0000, "temp": "", "time": "", "uptime": "", "upsince": "", "header": "", "load": ""}

HTMLPayloads = """
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <title>Raspberry Pi 3b at home.</title>
    </head>
    <body>
    <h1>Some readings from my Raspberry Pi 3b and it's "UPS"</h1>
    Prensented by <a href="https://front.the42.info">the42game</a> via <a href="https://gist.github.com/theskanthunt42/02de49d7190eb4a0a867d66c2e532e10">SimpUPSMon</a>
    <hr>
    <b>General Infomation</b>
    <br>
    The time is:
    <br>
    {timenow}
    <br>
    This Server has been up for: {uptime} 
    <br>
    Since {upsince}
    <br>
    BCM2837 SoC Temp: {temps}
    <br>
    Load Average: {LoadAvg}
    <br>
    <b>Current readings from the UPS:</b>
    <br>
    Battery Voltage: {volt}V
    <br>
    Battery Percentage: {percent}%
    <br>
    <b>Even more infomations from your side:</b>
    <br>
    "Backend" IP address is :{addr}:{port}
    <br>
    <b>YOUR</b> IP address is: <a href="https://ip.sb/ip/{RealAddr}">{RealAddr}</a>
    <br>
    You are connected from this Cloudflare CDN: {CfCDNIP}
    <br>
    Which should be located in: {CfCDNLOC}
    <br>
    Your headers: 
    <br>
    {header}
    <br>
    </body>
    
</html>
"""



def VisitorsOfTheRun():
    # WIP
    return None    

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
    ProDict = {"Origin": "", "CfIP": "", "CfCountry": ""}
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
        else:
            pass
    return ProDict

def SimpHTTPSend(client, address, assets):
    IncomingData = client.recv(1024)
    #print(f"Incoming connection from: {address}")
    #print(f"With header of {IncomingData}")# For debug and for fun, seems to be causing trouble
    ProDict = SimpHeaderRead(IncomingData)
    #RealIP = IncomingString.split("\r\n")[-5].split(": ")[1]
    #CfIP = IncomingString.split("\r\n")[8].split(": ")[1]
    #CfCountry = IncomingString.split("\r\n")[9].split(": ")[1]
    print(f"Incoming traffic from{ProDict['Origin']}")
    Response = HTMLPayloads.format(
        LoadAvg = assets["load"], RealAddr = ProDict["Origin"], CfCDNIP = ProDict["CfIP"], CfCDNLOC = ProDict["CfCountry"], 
        addr = address[0], port = address[1], volt = assets["voltage"], percent = assets["capacity"], temps = assets["temp"], 
        timenow = assets["time"], uptime = assets["uptime"], upsince = assets["upsince"], header = IncomingData.decode()
    )
    client.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    client.sendall(bytes(Response.encode("utf-8")))
    #client.sendall(b"<html>Hello.</html>")
    #print("Data sent.")
    

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


def main():
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
            client, address = s.accept()
            assets["voltage"] = BatteryPackVoltage(bus)
            assets["capacity"] = BatteryPackCapacity(bus)
            assets["temp"] = VCTempRead()
            assets["upsince"], assets["uptime"], assets["time"], assets["load"] = TimeRelated()
            SimpHTTPSend(client, address, assets)
            client.close()
        except OSError as error:
            client.close()
            break
        except KeyboardInterrupt:
            client.close()
            print("Interrupt by user.")
            break



if __name__ == "__main__":
    main()

