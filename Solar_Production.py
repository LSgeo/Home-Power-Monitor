## OLD WORKING VERSION - SEE DESKTOP FOR NEW VERSION THAT DOESNT WORK JUST YET :)
## ACTUALLY FORK - NO WEATHER BUT WORKS
import urllib, re, json, time, os.path
from datetime import datetime, timedelta
import numpy as np
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt
import pandas as pd

envoy = 'http://10.0.0.2/production.json' #IP of Enovy s energy meter
delay = 2 ## Seconds, delay between measurements
timer = 0
print('Program Running...')
first_run = True


while True:
## Getting data off Envoy S
    curr_str = urllib.request.urlopen(envoy).read().decode() # get html object, read it and decode it from byte to str
    jstruct = json.loads(curr_str) #interpret the json structure
#print(json.dumps(jstruct, sort_keys=True, indent=4)) #Pretty Print the structure
    cons_wnow = jstruct['consumption'][0]['wNow'] #Consumption watts now. Held in JSON structure, consumption field, (0 is 1st field), tagged wNow.
    prod_wnow = jstruct['production'][1]['wNow'] # Production watts now.
    enet_wnow = jstruct['consumption'][1]['wNow'] #Net power usage calculated on envoy
    cnet_wnow = cons_wnow - prod_wnow

## Weather integration, using Dark Sky API

## GPIO - The kicker  

    #nice_str = ('Consumption: '+str(cons_wnow)+', Production: '+str(prod_wnow)+', Net: '+str(enet_wnow))
    #print(nice_str)
    
## Print to Text File
    name_date = time.strftime('%d_%m_%Y')
    yname_date = datetime.strftime(datetime.now() - timedelta(1), '%d_%m_%Y')
    log_path  = ('/home/pi/Desktop/Logs/solar_log_%s.txt' %name_date)
    ylog_path = ('/home/pi/Desktop/Logs/solar_log_%s.txt' %yname_date)
    if os.path.exists(log_path) == False: #Make a new file for a new date
        newfile = open(log_path, 'w')
        newfile.write('Consumption, Production, Net,H:M:S'+'\n') #write header for new data
        newfile.close()
        print('Writing to new file!' + log_path)
    text_num = (str(cons_wnow) + ', ' + str(prod_wnow) + ', ' + str(enet_wnow))
    txt_file = open(log_path, 'a')
    txt_file.write(text_num + ', ' + time.strftime(' %H:%M:%S') +'\n')
    txt_file.close()

## Displaying data
    if timer >= 60: # Redraw every Minute, set -1 to disable
        if first_run == False: # Close figure before creating new one every time, other than first
            plt.close()
        data = np.genfromtxt(log_path, delimiter=',', skip_header=1, names=['Consumption', 'Production', 'Net'], usecols = (0,1,2))
        ydata = np.genfromtxt(ylog_path, delimiter=',', skip_header=1, names=['Consumption', 'Production', 'Net'], usecols = (0,1,2))
        timestamp = np.loadtxt(log_path, dtype = 'U', delimiter=',', skiprows=1, usecols = (3))
        times = [datetime.strptime(t, ' %H:%M:%S') for t in timestamp]
        ytimestamp = np.loadtxt(ylog_path, dtype = 'U', delimiter=',', skiprows=1, usecols = (3))
        ytimes = [datetime.strptime(t, ' %H:%M:%S') for t in ytimestamp]
        x = mpl.dates.date2num(times)
        yx = mpl.dates.date2num(ytimes)
        tfmt = mpl.dates.DateFormatter(' %H:%M:%S')
        #x = np.arange(data['Net'].size)
        plt.clf
        fig = plt.figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        plt.title('Envoy Power Data - %s' %name_date )
        plt.axhline(y=0, color='0.8')
        plt.plot(x,-data['Net'],'0.5',x,data['Production'],'c-',x,-data['Consumption'],'orange',yx,ydata['Production'],'g:')
        #plt.plot(yx,-ydata['Net'],'red',yx,ydata['Production'],'red',yx,-ydata['Consumption'],'red')
        ax.xaxis.set_major_formatter(tfmt)
        plt.text(0, 0, 'Current Usage: W',fontsize=40)
        plt.legend(['Net now: %s' %-enet_wnow,'Net','Production','Consumption','Production Yesterday'])
        plt.xlabel('Time')
        plt.ylabel('Watts')
        fig.add_subplot(111).axis(xmin=pd.Timestamp('1900-1-1 00:00:00'), xmax=pd.Timestamp('1900-1-1 23:59:59')) # there're also ymin, ymax
        ax.set_xlim(pd.Timestamp('1900-1-1 00:00:00'), pd.Timestamp('1900-1-1 23:59:59')) #Earlier conversion of datetime sets day to 1/1/1900, so our data plots to 1/1/1900
        plt.grid(b=True, which='major', color='0.9', linestyle='-')
        #plt.draw(fig)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show(block = False)
        #plt.savefig('/home/pi/Desktop/Solar.png', bbox_inches='tight', dpi=150)
        #print('Img saved')
        timer = 0

## Tidy up

    timer += delay ## Timer to update some things occasionally
    time.sleep(delay)
    first_run = False
