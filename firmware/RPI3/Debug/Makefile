###############################################################################
# Makefile for project 
###############################################################################

## General options
PROJECT = 
MCU = RPI3
COMPILER = "Python 3 (Proteus)"
TARGET = Debug
SHELL = C:\WINDOWS\system32\cmd.exe

## Tools general options

## Processing Tools
FLOWCHART=
MKPYTHON=mkpython.exe
#  C:/Users/DELL/Videos/IOT Sudoku/firmware/RPI3/Debug/Debug.pyz: TOOL=MKPYTHON
#     C:/Users/DELL/Videos/IOT Sudoku/firmware/Raspberry Pi 3/main.py

# Build tree:
all:	Debug

Debug:	Debug.pyz

Debug.pyz:	../../Raspberry\ Pi\ 3/main.py 
	$(MKPYTHON) "../../Raspberry Pi 3/main.py" -l "C:\Program Files (x86)\Labcenter Electronics\Proteus 8 Professional\DATA\VSM Studio\drivers\RaspberryPi" -z "Debug.pyz"

# tidy - delete all temporary files which are not involved in the target generation
tidy:

# cleanup - delete all generated files
clean:	tidy
	rm -rf Debug.pyz
