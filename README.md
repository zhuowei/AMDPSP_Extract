# AMDPSP_Extract: Extract AMD Secure Processor components from a BIOS image

## Usage

`pip install -r requirements.txt`

then

`python3 amdpsp_extract.py <bios>`

And it should create a bunch of ".bin" files corresponding to each 

Tested with Asrock X370 Taichi's BIOS v3.20 (https://www.asrock.com/mb/AMD/X370%20Taichi/#BIOS, sha256=5954cf5ee583b790ad26b356857a430848038e3c1666f86d7f30c0295308926d)

## Thanks

This uses Coreboot's definitions of the PSP directory structs: https://github.com/coreboot/coreboot/blob/master/src/vendorcode/amd/pi/00670F00/Proc/Psp/PspBaseLib/PspDirectory.h
