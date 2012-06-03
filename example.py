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
#print dates
#print weights
#this makes the data plot from left to right with 
#the newest data at the right
#FIXME use pandas to plot this as a timeseries
plt.plot(dates,weights,'-o')#super simple plotting on one axis
plt.ylabel('Weight(lbs)')
plt.show()

