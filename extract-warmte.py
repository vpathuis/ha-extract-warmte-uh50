import appdaemon.plugins.hass.hassapi as hass
import serial
import re
import requests
import datetime
from time import sleep

#
# App for reading Landis+Gyr UH50 warth installation. 
# Attention: if test = 1 is set the device will not be read, it will just test if the script is working.
#

class UH50(hass.Hass):

  def initialize(self):
    self.log("Initialize UH50")
    self.run_once(self.ReadUH50, "22:00:00")
    self.log("Waiting for 22:00 to read UH50 ... ")

  def ReadUH50(self, kwargs):
    self.log("Time to start extracting data from UH50")
    test = 0
    self.log("Test = " + str(test))
    if test == 1:
        stubfile = "stub_warmte.txt"
        try:
            f = open(stubfile, 'w')
            f.write("6.8(0255.987*GJ)6.26(02458.16*m3)9.21(66153690)")
            f.write("6.26*01(02196.39*m3)6.8*01(0233.431*GJ)\n")
            f.write("F(0)9.20(66153690)6.35(60*m)\n")
            f.write("6.6(0022.4*kW)6.6*01(0022.4*kW)6.33(000.708*m3ph)9.4(098.5*C&096.1*C)\n")
            f.write("einde\n")

        finally:
            f.close()    

        conn = open(stubfile, 'r')

    if test !=  1:
        conn = serial.Serial('/dev/ttyUSB0',
                            baudrate=300,
                            bytesize=serial.SEVENBITS,
                            parity=serial.PARITY_EVEN,
                            stopbits=serial.STOPBITS_TWO,
                            timeout=1,
                            xonxoff=0,
                            rtscts=0
                            )
        # Wake up
        conn.setRTS(False)
        conn.setDTR(False)
        sleep(5)
        conn.setDTR(True)
        conn.setRTS(True)
        # send /?!
        conn.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A")

        sleep(1.5)
        #Initialize
        self.log("Initialisatie op 300 baud")
        ir_command='/?!\x0D\x0A'
        conn.write(ir_command.encode('utf-8'))
        conn.flush()
        #Wait for initialize confirmation

        # Read at 300 BAUD, typenr
        self.log(str(conn.readline()))

        # Now switch to 2400 BAUD
        conn.baudrate=2400

    iteration = 0
    ir_line = ''
    ir_lines = ''
    GJ = ''
    m3 = ''
    foutcode = ''

    # Keep reading till we have what we need, or otherwise till the very end
    try:
        while ir_line != b'' and  GJ == '' and iteration < 100:
            iteration += 1
            ir_line = conn.readline()
            self.log(str(ir_line))
            ir_lines+=str(ir_line)

            # search for something that looks like this: 6.26*01(02196.39*m3)6.8*01(0233.431*GJ)
            searchObj = re.search( r'6.8\((.*)\*GJ\)6.26\((.*)\*m3\)9.21\(66153690\)', str(ir_line), re.M|re.I)

            if searchObj:
            #   1st result is GJ, 2nd is m3.  
                GJ = searchObj.group(1) 
                m3 = searchObj.group(2)
                self.log ("GJ: " + GJ)
                self.log ("m3: " + m3)

    finally:
        conn.close()
    
    self.SendWarmteReading(GJ, m3)

  # the next part is not related to the device, but should be adjusted to your situation
  def SendWarmteReading(self, GJ = "", m3 = ""):
    self.log("Sending warmte reading")
    api = "<<put url here>>/warmte-bijwerken-api/"
    today = datetime.date.today().strftime('%Y-%m-%d')
    winter = "" # not implemented yet
    temp = "" # not implemented yet
    foutcode = "" # not implemented yet
    param = '?date=' + today + '&winter=' + winter + '&temp=' + temp + '&GJ=' + GJ + '&m3=' + m3 + '&foutcode=' + foutcode
    url = api + param
    self.log('calling url: ' + url)
    r = requests.get(url)
    self.log("Finished sending")
