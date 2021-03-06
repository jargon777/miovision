# Miovision Data API Scraper
This program may be prone to bugs, it is not fully tested.
For now, this is a console application, you interact with it by typing the number for options it shows.

## Included in this repository
In this repository, you will find
* This help file
* The script file
* An executable version of the script (see the "exe" folder)
* Sample exports for all the options available from the API as of 2017 08 12

## Installing Python
This script is written in Python 3, and has been tested on the 64 bit version of python 3.5. Python 3.5 is available at this link: https://www.python.org/downloads/release/python-354/ 

The 64 bit version tested is the Windows x86-64 executable installer (https://www.python.org/ftp/python/3.5.4/python-3.5.4-amd64.exe)

### Dependancies
After installing python, you will need to install the following dependancies
* boto3
* warrant

If you installed python correctly, you should be able to type "python" and "pip" in the command console to access python and the python package installer (type command in the start menu to open it). 

To install these required packages, type "pip install boto3" for example from your command line.

Before installing "warrant" you should install pycrypto, as it is a dependancy of warrant and likely will not compile on your system. You can download "pycrypto-2.7a1-cp35-none-win_amd64.whl" from the "dependancies" folder of this repository, and then type "pip install C:\pycrypto-2.7a1-cp35-none-win_amd64.whl" where C:\pycrypto-2.7a1-cp35-none-win_amd64.whl corresponds to where you saved the wheel. After doing this, you can then proceed to do "pip install warrant".

## Running the Application with the Executable
Ensure that a "credentials.json" file is placed in the same folder with the application. Double click the application to run, you should get a console screen with the main option bridge.

## Running the Application in Python
Navigate to the folder where you downloaded "main.py" and type "python main.py". This should run the program in your command window. If you get errors before seeing the main menu, it is likely that some dependancy is still missing.

## Data Export Format
Data is exported in CSV format. The code usually highlights how the data is exported if you read the comments, otherwise:
* In the "signal statuses" and the "detector status" files, "channels" refer to how miovision/waterloo organises the data, not every channel is used, so the columns don't always have useful data. 
* In these files, POSIX refers to the unix timestamp, and is the last column
* In these files, signal-status shows red/yellow/green for the signal group (channel) attached to it. You will have to query Intersection Configuration to figure out the signal grouping or make guesses yourself.
* In these files, detector status shows TRUE if a vehicle is detected and FALSE otherwise.