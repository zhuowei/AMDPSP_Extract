import sys
import enum
import zlib
from construct import *

spiFlashOffset = 0xff000000

# https://github.com/coreboot/coreboot/blob/master/src/vendorcode/amd/pi/00670F00/Proc/Psp/PspBaseLib/PspDirectory.h

PSP_DIRECTORY_HEADER = Struct(
    "PspCookie" / Int32ul,
    "Checksum" / Int32ul,
    "TotalEntries" / Int32ul,
    "Reserved" / Int32ul,
)

PSP_DIRECTORY_ENTRY = Struct(
    "Type" / Int32ul,
    "Size" / Int32ul,
    "Location" / Int64ul,
)

class PSP_DIRECTORY_ENTRY_TYPE(enum.Enum):
    AMD_PUBLIC_KEY                  = 0x00           #< PSP entry pointer to AMD public key
    PSP_FW_BOOT_LOADER              = 0x01           #< PSP entry points to PSP boot loader in SPI space
    PSP_FW_TRUSTED_OS               = 0x02           #< PSP entry points to PSP Firmware region in SPI space
    PSP_FW_RECOVERY_BOOT_LOADER     = 0x03           #< PSP entry point to PSP recovery region.
    PSP_NV_DATA                     = 0x04           #< PSP entry points to PSP data region in SPI space
    BIOS_PUBLIC_KEY                 = 0x05           #< PSP entry points to BIOS public key stored in SPI space
    BIOS_RTM_FIRMWARE               = 0x06           #< PSP entry points to BIOS RTM code (PEI volume) in SPI space
    BIOS_RTM_SIGNATURE              = 0x07           #< PSP entry points to signed BIOS RTM hash stored  in SPI space
    SMU_OFFCHIP_FW                  = 0x08           #< PSP entry points to SMU image
    AMD_SEC_DBG_PUBLIC_KEY          = 0x09           #< PSP entry pointer to Secure Unlock Public key
    OEM_PSP_FW_PUBLIC_KEY           = 0x0A           #< PSP entry pointer to an optional public part of the OEM PSP Firmware Signing Key Token
    AMD_SOFT_FUSE_CHAIN_01          = 0x0B           #< PSP entry pointer to 64bit PSP Soft Fuse Chain
    PSP_BOOT_TIME_TRUSTLETS         = 0x0C           #< PSP entry points to boot-loaded trustlet binaries
    PSP_BOOT_TIME_TRUSTLETS_KEY     = 0x0D           #< PSP entry points to key of the boot-loaded trustlet binaries
    PSP_AGESA_RESUME_FW             = 0x10           #< PSP Entry points to PSP Agesa-Resume-Firmware
    SMU_OFF_CHIP_FW_2               = 0x12           #< PSP entry points to secondary SMU image
    PSP_S3_NV_DATA                  = 0x1A           #< PSP entry pointer to S3 Data Blob
    AMD_SCS_BINARY                  = 0x5F           #< Software Configuration Settings Data Block

def dumpOneSegment(indata, dirEntry):
    print(dirEntry)
    if dirEntry.Size == 0xffffffff:
        return
    fileOff = dirEntry.Location - spiFlashOffset
    try:
        segmentTypeName = PSP_DIRECTORY_ENTRY_TYPE(dirEntry.Type).name
    except ValueError:
        segmentTypeName = "Unknown_" + hex(dirEntry.Type)
    filename = segmentTypeName + ".bin"
    with open(filename, "wb") as outfile:
        outfile.write(indata[fileOff:fileOff + dirEntry.Size])
    if fileOff + 0x100 < len(indata) and indata[fileOff + 0x100] == 0x78:
        # zlibbed
        zlibOff = fileOff + 0x100
        outdat = zlib.decompress(indata[zlibOff:])
        with open(segmentTypeName + "_decompressed.bin", "wb") as outfile:
            outfile.write(outdat)

def analyzePSP(indata, pspOffset):
    dirHeader = PSP_DIRECTORY_HEADER.parse(indata[pspOffset:])
    print(dirHeader)
    dirEntries = PSP_DIRECTORY_ENTRY[dirHeader.TotalEntries].parse(indata[pspOffset + PSP_DIRECTORY_HEADER.sizeof():])
    print(dirEntries)
    for dirEntry in dirEntries:
        dumpOneSegment(indata, dirEntry)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 amdpsp_extract.py <path to bios>")
        return
    with open(sys.argv[1], "rb") as infile:
        indata = infile.read()
        pspOffset = indata.find(b"$PSP")
        analyzePSP(indata, pspOffset)

if __name__ == "__main__":
    main()