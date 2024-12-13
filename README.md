## Install dependencies
```bash
python3 -m venv venv
source venv/vin/activate

// for _mqtt.py
pip install python-dotenv awsiotsdk

// for read_GIPS_uwb.py
pip install pyserial pandas numpy
```

## Run code (_mqtt.py)
```bash
python3 _mqtt.py
```

## Run code (read_GIPS_dist.py)
**Please note that the COM port setting may need adjustment**
**Checkout the true port name**
On Unix-like system, a simple check can be done with```ls /dev/ttyUSB*```

### On rpi:
```bash
python3 read_GIPS_distance.py
```
### On wsl: bind port first!
In windows PowerShell:
```bash
usbipd list
usbipd bind --busid <busid> // with manager permission
usbipd attach --wsl --busid <busid>
```
check [this website](https://learn.microsoft.com/zh-tw/windows/wsl/connect-usb) for installation and more information about usbipd.

In wsl:
```bash
sudo venv/bin/python read_GIPS_distance.py
```
