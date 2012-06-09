from withings import * 
import numpy as np
import matplotlib.pyplot as plt #for plotting weights
#-----------------------------------
#get your consumer key and secret after registering 
#as a developer here: https://oauth.withings.com/en/partner/add
consumer_key='your_consumer_key_here_1111111111111111111111111111111111111111'
consumer_secret='your_consumer_secret_here_1111111111111111111111111111111111111111111'
#the first argument here is the email address you used to register
#for a Withings developer account
wobj=Withings('your_registered_email_address@example.com',consumer_key,consumer_secret)
(dates,weights)=wobj.get_weights()
print "You have ",len(weights)," weight measurements recorded"
#pandas allows to build a timeseries object which will display
#dates along the x-axis when plotted and can have rolling window 
#functions applied to it, like rolling_mean,rolling_median,rolling_std,etc.
rdates=[datetime.fromtimestamp(i) for i in dates]
ts=Series(weights,index=rdates)
#the marker='o' option will put a dot at each measurement point
#which, if you mouse-over will display the value
ts.plot(marker='o',color='b')
plt.ylabel('Weight(lbs)')
plt.show()
#this will overlay a smoothed curve which suggests the trend
#of the underlying data
rolling_mean(ts,len(weights)/float(7)).plot(color='r',linewidth='3')
#if you don't have pandas, or have problems installing it,
#the code below makes a basic plot without the nice date labels
#on the x-axis
#plt.plot(dates,weights,'-o')#super simple plotting on one axis
#plt.ylabel('Weight(lbs)')
#plt.show()

