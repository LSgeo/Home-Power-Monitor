/* Arduino example code for DHT11, DHT22/AM2302 and DHT21/AM2301 temperature and humidity sensors. More info: www.makerguides.com */
// Include the libraries:
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <SPI.h>
#include <Ethernet.h>

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(10, 0, 0, 123);

// Initialize the Ethernet server library
// with the IP address and port you want to use
// (port 80 is default for HTTP):
EthernetServer server(80);
// Set DHT pin:
#define DHTPIN 8
#define DHTTYPE DHT22   // DHT 22 
// Initialize DHT sensor for normal 16mhz Arduino:
DHT dht = DHT(DHTPIN, DHTTYPE);
int TankLvlIN = A0; // Tank Level  input pin (0.1 to 5.0 Volt)
float TankLevelRaw = 0.0;  // Variable to Store Tank Level
float TankLevel = 0.0;  // Variable to Store Tank Level

void setup() {
  // Begin serial communication at a baud rate of 9600:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Ethernet WebServer");
  dht.begin();
  // start the Ethernet connection and the server:
  Ethernet.init(10);  // Most Arduino shields
  Ethernet.begin(mac, ip);
  server.begin();
  Serial.print("Server is at ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  // listen for incoming clients
  EthernetClient client = server.available();
  if (client) {

    // Initial HTML
    Serial.println("new client");
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println("Refresh: 5");  // refresh the page automatically every 5 sec
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          // Wait a few seconds between measurements:
          delay(2000);
          // Reading temperature or humidity takes about 250 milliseconds!
          // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
          // Read the humidity in %:
          float h = dht.readHumidity();
          // Read the temperature as Celsius:
          float t = dht.readTemperature();
          TankLevelRaw = analogRead(TankLvlIN);
          TankLevel = ((TankLevelRaw-171)/682)*100

          // Check if any reads failed and exit early (to try again):
          ;if (isnan(h) || isnan(t)) {
            Serial.println("Failed to read from DHT sensor!");
            client.stop();
            return;
          }
          client.print("Temperature: ");
          client.print(t);
          client.print(" DegC. Humidity: "); 
          client.print(h);
          client.print(" %. Tank Level: ");
          client.print(TankLevelRaw);
          client.print(" ~~~ ");
          client.print(TankLevel);
          client.print(" %.");
          client.println("<br />");
          client.println("</html>");
          break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        } else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    Serial.println("client disconnected");
  }
}
