SETTINGS_FORM = b"""\
HTTP/1.0 200 OK
<html>
 <head>
  <title>Project X config page</title>
 </head>
 <body>
  <form method="post">
   Enter SSID and password:</br>
   SSID:&nbsp;<input name="ssid" type="text"/></br>
   Password:&nbsp;<input name="pass" type="password"/></br>
   <input type="submit" value="Submit">
  </form>
  <form method="post">
   Enter ThingSpeak key:</br>
   Key:&nbsp;<input name="key" type="text"/></br>
   <input type="submit" value="Submit">
  </form>
 </body>
</html>
"""

SETTINGS_BYE = b"""\
HTTP/1.0 200 OK
<html>
 <head>
  <title>Project X config page</title>
 </head>
 <body>
  <p>The board is going to reboot, and try to connect to specified network.</p>
 </body>
</html>
"""


# a template of HTTP request to ThingSpeak to post temperature and humidity
THINGSPEAK_POST_TEMPLATE = """
POST /update HTTP/1.1
Host: api.thingspeak.com
Connection: close
X-THINGSPEAKAPIKEY: %s
Content-Type: application/x-www-form-urlencoded
Content-Length: %d
%s
"""