# JQ6500-tool
Tool for uploading and downloading JQ6500 MP3 voice mdoule

This one: https://www.elecfreaks.com/wiki/index.php?title=JQ6500_Mini_MP3_Module

Install python-scsi first: https://github.com/rosjat/python-scsi.git

[ 3681.857961] usb 4-2: new full-speed USB device number 6 using uhci_hcd
[ 3682.038066] usb 4-2: New USB device found, idVendor=e2b8, idProduct=0811
[ 3682.038069] usb 4-2: New USB device strings: Mfr=1, Product=2, SerialNumber=1
[ 3682.038071] usb 4-2: Product: CD002
[ 3682.038073] usb 4-2: Manufacturer: CD002
[ 3682.038075] usb 4-2: SerialNumber: CD002
[ 3682.040151] usb-storage 4-2:1.0: USB Mass Storage device detected
[ 3682.040648] scsi host8: usb-storage 4-2:1.0
[ 3683.066138] scsi 8:0:0:0: Direct-Access     CAI      CD002-1          1.00 PQ: 0 ANSI: 0
[ 3683.069142] scsi 8:0:0:1: CD-ROM            YULIN     PROGRAMMER      4.05 PQ: 0 ANSI: 2
[ 3683.070182] sd 8:0:0:0: Attached scsi generic sg4 type 0
[ 3683.082134] sd 8:0:0:0: [sdd] Attached SCSI removable disk
[ 3683.089179] sr 8:0:0:1: [sr1] scsi-1 drive
[ 3683.089479] sr 8:0:0:1: Attached scsi CD-ROM sr1
[ 3683.089608] sr 8:0:0:1: Attached scsi generic sg5 type 5

Memory map:
0x000000 - 0x03ffff  CD-ROM image
0x040000 - 0x1fffff  MP3 data

2MB flash