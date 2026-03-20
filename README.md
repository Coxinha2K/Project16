# Project16
A virtual and tiny Operating System made in Python

## What the frick is Project16???
Project16 is a tiny "operating system" made in Python by me, Coxinha2K.
Project16 exists because i always wanted to know how do a OS works, so i built Project16 because i didn't wanted to download QEMU and learn Assembly

## Some points of Project16
- Lightweight: version A10 fully installed has a FS of ~19KB
- Intuitive: you can enable debug mode in the `boot.cfg` file to enable some messages in Core16 (kernel) and Project16 (userland)
- Homemade: everything you see in Project16 (the whole thing itself) was hand-made, coded in some several weeks (version A10 was 4 weeks)

## Why would i use Project16?
If you are like me and want to learn how a OS works, i think Project16 is a good choice, because:

- Machine16 is like your real hardware, it loads the filesystem, runs the bootloader (in A10, M16 IS the bootloader so it runs the kernel instead) and do stuff happen
- RetroFS is a stoopid easy thing to work with, since it uses JSON as encoding and the structure is easy (i'll update it, no worry)
- Core16 is your kernel, which handles the recovery mode, also called CSRE (Core System Recovery Environment) and Project16 (the userland)
- Project16 is such a extensible thing, since it is easy to work with
