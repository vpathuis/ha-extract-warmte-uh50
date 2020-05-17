Version 0.1 Devepment Version!
Install on Home Assistant with AppDaemon and include the pyserial python package in the configuration.

tweak the following:
-  time to run on. Warning: each call will cost the device a couple of minutes of battery on which it's supposed to run on for 11 years, so don't run this script often
- serial port for the cable to the UH50
- tweak how you'll use the data (GJ & m3). I send it to a local API
- test first with "test = 1"

The script is optimized to save battery and will therefore stop after finding the desired results. There is more info coming out though if you don't stop the script, should you need it.
