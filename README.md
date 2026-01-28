# SimpUPSMon is a tool I wrote for my own use.
This is the GitHub repository behind my [Raspberry Pi + UPS Monitor](https://front.the42.info/rpimon)  

I run it on my Raspberry Pi 3b sitting at home and use [frp](https://github.com/fatedier/frp) to forward requests to a remote server and serve it on that page.  
This is my own little hobbist project began as a small thought during a review of my past Gist Projects and well it began as a small little script on [gist](https://gist.github.com/theskanthunt42/02de49d7190eb4a0a867d66c2e532e10) as well, but my friend reckon I should turn it as a actual repo for easy management etc. so I did.  

## How to use it?

Well... First you needs to have a Raspberry Pi 1/2/3/4b, then connect it (via GPIO via pogo pins) to this [tiny "UPS" module](https://github.com/linshuqin329/UPS-18650) and enable I2C, and this module's [MAX17040G](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17040-MAX17041.pdf) (which is basicaly a 2-cell Battery Fuel Gauge + Model Gauge for rechargeable Li-ion, in this case 2 x 18650), and it would probably on I2C bus 1(that is `i2c-1`) with address `0x36`, then we talk.

# Features

- Checking my servers(aka Raspberry Pi 3b) and UPS status.
- Read your Requests and Headers sent by your browser.
- Read your IP provided by Cloudflare.
- Check out which Cloudflare CDN node you used to access this page.
- I wrote the HTTP "server" (that sent and receieve datas) from scratch using socket only.
- Me having fun.

# TODO for me

- [ ] **MULTIPLEXING THE SERVER.**
- [ ] Getting rid of those comment out functions which mostly are being use during testings?
- [ ] Better ways to test and deploy.
- [ ] Add more fun features!!!
- [x] See how far BCM2837(aka the Raspberry Pi 3b) can go in 10-ish years after it's launch.
For the last one tho, it still runs rather snappy till your run anything related to File I/O like apt.

# Anything else?

I've got tons of ambitious thoughts on this project, even more things to do other than RPI itself and UPS, might have some features related to SDR and Satellite Weather Imagery later on lol, I've got LNA and BPF ready but still experimenting with antennas(which... is kinda hard for me now to get a big grid dish on roof right now, but trust me, probably will demo it in later Q1 2026)  

There's also a power source detection feature on this module but I am not bothering to implement it yet since I am lazy to grab my soldering iron and solder that two joints on the back of the module to enable it anyway.  

Any maybe Weather Stations...? I don't know. Just still thinking what can I add to this. LoRA as well? Maybe? or some randomly capture pics everyday? Idk

# Why I am doing all this

Well, this very Raspberry Pi 3b is my first computer that I got for use by me only, and I had it with me during some very difficult/dark days during Junior Highs, I used it as a general purpose computer you know? And tons of memories with it incl. using my right-hand thumb and the blood vessel in it to cool it down while playing [SuperTuxKart](https://supertuxkart.net/Main_Page.html) *yes singel hand drive*. So this piece of hardware is special to me.  
And being my first actually own computer, it's also my first ARM computer, and now I am typing this README and writing the codes on a M4 Mac mini which is also ARM-based, you get the point.

# Credits

- Me: Writing the code.
- Python: The great language that's popular and easy to write even for someone like me who is not Computer Science related major.
- Visual Studio Code: The IDE in use, tho I debug on the actual hardware
- Raspberry Pi Foundation: Hardware in use. Could we at least get H.264 hardware encoding/decoding please? And more PCIe Lanes please. Oh and can you guys starts to shifting away from Broadcom SoCs? Please... You're making your own southbridges and MCUs.
- macOS and Mac mini: For allowing me doing intensive R&D w/o messing with other things, also macOS for being Unix, I hate writing codes on Windows, but don't have a fully built-out PC for Linux back at home.
- Caddy: Reverse proxying and hosting my blog plus this project's page.
- frp: frp does the forwarding pages to my server running Caddy at front.
- Cloudflare: For CDN services.
- GitHub: Hosting this Git repo.


# Special Thanks To:
- My friends: For providing me feedbacks and ideas and possible solutions to the problems and warning me about potential problems.
- All the people who shared how they resolve problems online on a webpage or stackoverflow.
- All the people out there that still doing things without AI or by asking AI problems to let them search, including me.


This project is 100% No AI.

