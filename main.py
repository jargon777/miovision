import boto3
import json, csv
from warrant.aws_srp import AWSSRP
from urllib.request import urlopen
from urllib.request import Request
import time
import os

try:
    with open('credentials.json') as data:    
        credentials = json.load(data)
except:
    print("No credentials data provided! You need to include a credentials.json file in the same directory as the application/script.")
    exit()

USER_POOL_ID = 'us-east-1_jwgA3PBXm';
COGNITO_APP_ID = 'j5c2sgbkdkd4cd39hk7irkn70'; 
COGNITO_USERNAME = credentials['username'];
COGNITO_PASSWORD = credentials['password'];
clearConsole = lambda: os.system('cls')
ENCODEING = 'utf-8' #the encoding that the API returns, default is UTF
WRITEDIR = "exports/"
 
'''
THIS CODE's STARTING POINT IS FROM https://github.com/Miovision/open-data-api-client-example/tree/master/python
This is a dirty implementation of data scraping.
Program Flow:

OPTION BRIDGE - Select the action you want to do
--> 1 : This option bridges to the location dumper, it will create a CSV with all the intersections and id's available.
--> 2, 3, 4 : These opions bridge to a selector that can be used to select the ID you want data from
  |--> (Deck) Used to select the ID you want to get data for, will show you a list going from 0 to X for all the available intersections (cars) 
''' 
 

'''
++++++++++ MIOVISION SUPPLIED FUNCTIONS +++++++++++++++++++++++
'''
# After we're successfully signed in, make a request to get the list of intersections.  
# For more information about what APIs are available, visit http://docs.api.miovision.com/
def getData(idToken, url):
    #ACCPETS an idToken used to authenticate and a URL request id. Returns the data obtained from Miovision as an array parsed from JSON.
    req = Request(url) 
    req.add_header('Authorization', idToken)
    resp = urlopen(req)
    return json.loads(resp.read().decode(ENCODEING))

# Signs into cognito using the username/password passed in
def getToken(username, password):
    client = boto3.client('cognito-idp', region_name='us-east-1', 
        # avoid botocore.exceptions.NoCredentialsError
        aws_access_key_id='not required', aws_secret_access_key='not required')
    aws = AWSSRP(username=username, password=password, pool_id=USER_POOL_ID,
                 client_id=COGNITO_APP_ID, client=client)
    tokens = aws.authenticate_user()
    return tokens['AuthenticationResult']['IdToken']


'''
================= BRIDGE METHODS ===================
'''

def printExportIntersections(idToken):
    clearConsole() #clears the console (maybe)
    print("Fetcing Data...")
    intersections = getData(idToken, 'https://api.miovision.com/intersections')
    
    exportF = WRITEDIR + "intersections.csv" #the location where we save the data
    
    #use the CSV writer to export the data into CSV format.
    with open(exportF, 'w', newline="\n") as csvfile:
        csvfile = csv.DictWriter(csvfile, fieldnames=intersections[0].keys())
        csvfile.writeheader()
        csvfile.writerows(intersections)
    
    #dump the data to the screen
    print("------------ JSON DUMP OF INTERSECTION DATA -------------")
    print(json.dumps(intersections, indent=1, sort_keys=True))
    print("------- DATA EXPORTED TO EXPORTS/intersections.csv ------")
    input("Pressing Return will Return to the Option Bridge")
    clearConsole()
    
def bridgeGetIDreq(idToken, bridge):
    #method switches based on the requested option bridge. Handles options 2-4.
    deck = None #the sub-option chosen at this level.
    print("Input ID Manually or Select from List of Names & Locations\n-------------------------------------------------")
    print("1 - Select from List")
    print("2 - Type Manually")
    deck = input("? - ")
    #try catch designed to loop you back to the menu. 
    try: 
        if deck == '1':
            #generate the list of intersections as in printExportIntersections, but save the id's for use in the URL, and associate them with a number so they can be chosen from the menu.
            print("Fetching Intersection List...")
            intersections = getData(idToken, 'https://api.miovision.com/intersections')
            
            car = 0 #the intersection ID 
            clearConsole()
            print("Choose ID\n-------------------------------------------------")
            for item in intersections:
                print(str(car) + " " + item["name"] + " (" + item["id"] + ")")
                car += 1
            car = int(input("? - "))
            car = intersections[car]["id"] #convert the option to ID for passing, if error, the catch will return you to the menu.
    
        elif deck == '2':
            print("Type ID in Console\n-------------------------------------------------")
            car = input("? - ")
        else:
            raise #invalid input option selected
        
        #switch to the correct followup option based on the bridge. Option 3 and 4 share a method.  
        if bridge == '2':
            if not printExportIntersectionConfig(idToken, car): raise
        elif bridge == '3':
            if not bridgeIntersectionHistory(idToken, car, "signal-statuses"): raise
        elif bridge == '4':
            if not bridgeIntersectionHistory(idToken, car, "detector-statuses"): raise
    except:
        #raise #comment this line to silently ignore errors and loop back to the start.
        clearConsole()
        print("Invalid Option or some other error.")
        bridgeGetIDreq(idToken, bridge) #callback for error
        
'''
================== CAR METHODS ======================
'''

def printExportIntersectionConfig(idToken, car):
    clearConsole()
    print("Fetching Intersection Configuration")
    url = 'https://api.miovision.com/intersections/' + str(car)
    intersections = getData(idToken, url)
    
    #dump the highest level of the configuration JSON
    exportF = WRITEDIR + "configuration-base-" + str(car) + ".csv"
    with open(exportF, 'w', newline="\n") as csvfile:
        csvfile = csv.DictWriter(csvfile, fieldnames=intersections.keys(), extrasaction='ignore')
        csvfile.writeheader()
        csvfile.writerow(intersections)
    
    
    #phasing information is also provided as another nested array, here we dump it to a seperate file if available.
    if len(intersections["phases"]) > 0:
        exportF = WRITEDIR + "configuration-phases-" + str(car) + ".csv"
        with open(exportF, 'w', newline="\n") as csvfile:
            csvfile = csv.DictWriter(csvfile, fieldnames=intersections["phases"][0].keys(), extrasaction='ignore')
            csvfile.writeheader()
            csvfile.writerows(intersections["phases"])
    else:
        print("This intersection has no phases listed.")
    
    #detector information is also provided as another nested array, here we dump it to a seperate file if available.
    if len(intersections["detectors"]) > 0:
        exportF = WRITEDIR + "configuration-detectors-" + str(car) + ".csv"
        with open(exportF, 'w', newline="\n") as csvfile:
            csvfile = csv.DictWriter(csvfile, fieldnames=intersections["detectors"][0].keys(), extrasaction='ignore')
            csvfile.writeheader()
            csvfile.writerows(intersections["detectors"])
    else:
        print("This intersection has no detectors listed.")
    
    #dump the data to screen if requested.
    print("Type '1' to see a JSON dump of the data, otherwise press return to the Option Bridge")
    option = input("?")  
    if option != '1':
        print("------------ JSON DUMP OF INTERSECTION DATA -------------")
        print(json.dumps(intersections, indent=1, sort_keys=True))
        print("------- DATA EXPORTED TO EXPORTS/intersections.csv ------")
        input("Pressing Return will Return to the Option Bridge")
    clearConsole()
    return True
    
def bridgeIntersectionHistory(idToken, car, mode):
    clearConsole()
    #parameters used to configure the dump.
    start = 0  #timestamp of the start period
    end = start #timestamp of the end period, in this hacky method assigned to be identical to start, it seems miovision returns you the closes timestamp regardless of its validity.
    interval = 1000 #size of the step to take when searching for data, the resotion of the data seems to be about 1000 ms (1 second) for signal statuses, and about 20000 for detector statuses. 
    intervals = 1 #number of rows to return.
    exportF = WRITEDIR + mode + "-" + str(car) + ".csv"
    try:
        print("Current Unix Time is: " + str(int(time.time()) * 100))
        print("Choose a time stamp and interval size and count to obtain data")
        print("Some time combinations may not work, latest available data seems to be from before 1490894595394")
        print("Choose the end period of the data")
        print("Input as Unix Timestamp with Seconds (or press enter for default of 1490894595394")
        start = input("? - ")
        start = 1490894595394 if start == "" else int(start) #assign a default value when you press enter with no entry. 
        end = start #set start to equal end.
        
        print("Best interval seems to be 1000 for signal status and 10000 for detector status")
        print("Choose the interval size of the data in milliseconds (or press enter for default 1000 = 1 second)")
        interval = input("? - ")
        interval = 1000 if interval == '' else int(interval)
        
        print("Choose the number of intervals to obtain the data for (large values may take awhile)")
        intervals = int(input("? - "))
        
        dataprevtime = 0 #so we can check if the data is new for this interval
        i = 0 #the intervals we've completed are stored here
        break_cond = 0 #prevents infinite loops
        
        itemlist = [] #list holding the data we obtain
        max_len_item = 0 #used later when we write the data to file. Should always equal 0 if miovision's system returns identically formatted data.
        max_len = 0
        
        #loop until intervals done
        while i < intervals:
            #format the request URL and get the data
            url = 'https://api.miovision.com/intersections/' + str(car) + '/' + mode + '/historical?startTime=' + str(start) + '&endTime=' + str(end)
            data = getData(idToken, url)
            
            #get the timestamp so we can check things.
            datatime = str(data[0]["time"])
            
            #check if this is new or old data
            if datatime == dataprevtime:
                break_cond += 1 #if old data, increment the infinite loop protection.
                print("Data in this interval is identical to previous, adding one more interval")
                if break_cond > 5:
                    #the interval is probably too small, as the last few intervals got identical data.
                    print("Interval too small? Identical data returned for five intervals")
                    break
            else:
                break_cond = 0 #reset the infnite loop protector
                print("Data for: " + datatime + " obtained ")
                items = {} #use a dictionary to hold the data as we process it
                items["posix"] = datatime #store the timestamp as a heading called "posix"
                for item in data[0]["statuses"]:
                    key = "channel-" + str(item["channel"]) #convert the channel names to "channel-#".
                    if mode == "signal-statuses": items[key] = item["status"] #it seems for the statuses, there are two variables that hold the state of the sginal, here we are only saving the "status" one.
                    elif mode == "detector-statuses": items[key] = item["active"] #the detector status data, this is true/false for if the detector is activated.
                itemlist.append(items)
                if len(items) > max_len: #if we find a new item, check that it has the same configuration as previous items. We use the "largest" item to format the CSV, in case it has extra columns.
                    max_len = len(items)
                    max_len_item = len(itemlist) - 1
                i += 1
            
            dataprevtime = datatime    
            start -= interval #do the next interval
            end = start
        
        #write the data to file.
        with open(exportF, 'w', newline="\n") as csvfile:
            csvfile = csv.DictWriter(csvfile, fieldnames=sorted(itemlist[max_len_item].keys()), extrasaction='ignore')
            csvfile.writeheader()
            csvfile.writerows(itemlist)
            
    except:
        raise
        clearConsole()
        print("Invalid Input or output file already open, select option again!")
        bridgeIntersectionHistory(idToken, car)
        
    input("Pressing Return will Return to the Option Bridge")
    clearConsole()
    return True
    

'''
=================== TOPLEVEL METHODS =================
'''

def optionBridge(idToken):
    #loop into the main option selector.
    while 1:
        bridge = None
        print("SELECT COMMAND (Option Bridge)\n-------------------------------------------------")
        print(" 1 - Display & Export Intersection Names and Locations")
        print(" 2 - Display & Export Intersection Configuration")
        print(" 3 - Export Historical Intersection Signal Statuses")
        print(" 4 - Export Historical Intersection Detector Statuses")
        print(" 5 - Quit")
        bridge = input("? - ")
        if bridge == '1':
            printExportIntersections(idToken)
        elif bridge == '2' or bridge == '3' or bridge == '4':
            clearConsole()
            bridgeGetIDreq(idToken, bridge)
        elif bridge == '5':
            return
        else:
            optionBridge(idToken) #recursive error

def main():
    print("Loading & Verifying IDs...")
    idToken = getToken(COGNITO_USERNAME, COGNITO_PASSWORD) #login to miovision's system.
    print("Setting up Environment...")
    if not os.path.exists(WRITEDIR):
        os.makedirs(WRITEDIR)
    
    clearConsole()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nTHIS PROGRAM IS NOT BUGPROOF, in fact, it is probably bug-prone. If something weird happens, sorry.\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    optionBridge(idToken)



# Start the sign-in process if the script is run from this file.
if __name__ == "__main__":
    main()