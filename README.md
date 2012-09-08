pywithings
==========

#Requirements
Get your consumer key and secret after registering 
as a developer here: https://oauth.withings.com/en/partner/add

Install rauth:

    $ easy_install rauth

or

    $ pip install rauth

#Sample usage

    consumer_key = 'your_consumer_key'
    consumer_secret = 'your_consumer_secret_here'

    wobj = Withings('youremail@mail.com',consumer_key,consumer_secret)
    measurements = wobj.get_meas()
    (dates,weights) = wobj.get_weights(measurements,units="lbs")

That's it- at this point weights will contain an array of weight measurements and dates will be the dates on which those measurements were taken.

#API methods

###get_meas(self,devtype=0,startdate=None,enddate=None):
This method retrieves the raw json provided by withings getmeas API method which by default contains 
all measurement types unless the devtype parameter is specified:
0 = scale, blood pressure cuff, and height
1 = scale measurements only (weight and bodyfat related)
4 = blood pressure cuff only 
5 = both scale and blood pressure cuff

If specified, the startdate and enddate parameters must follow the format: '%Y-%m-%d'
'2012-12-25' for example


##Convenience methods
For all methods below the output of a call to get_meas should be used as the data argument

###get_weights(self,data,units="kg"):
Returns an array of dates and an array of weight measurements as (dates,weights), units may be "lbs" or "kgs"

###get_height(self,data,units="cm"):
Returns a date and a height, this should correspond to the height the user specified in their profile.

###get_fat_free_mass(self,data,units="kg"):
Returns an array of dates and an array of weight measurements as (dates,weights)

###get_fat_ratio(self,data):
Returns an array of dates and an array of percent values as (dates,ratios)

###get_fat_mass_weight(self,data,units="kg"):
Returns an array of dates and an array of weight measurements as (dates,weights)

###get_diastolic_blood_pressure(self,data):
Returns an array of dates and an array of diastolic blood pressure measurements in mmHg as (dates,pressures)

###get_systolic_blood_pressure(self,data):
Returns an array of dates and an array of systolic blood pressure measurements in mmHg as (dates,pressures)

###get_heart_pulse(self,data):
Returns an array of dates and an array of heart rate measurements in beats per minute as (dates,heart rates)

