#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqttServer = "broker.hivemq.com";
int port = 1883;
String stMac;
char mac[50];
char clientId[50];

WiFiClient espClient;
PubSubClient client(espClient);

#define PIR_PIN 13 
#define Relay_PIN 4
#define LDR_PIN 34
#define buzzer 18
#include "DHT.h"

#define DHTPIN 15 
#define DHTTYPE DHT22 

#define TEMP_UPPER_THRESHOLD  25 // upper temperature threshold
#define TEMP_LOWER_THRESHOLD  22 // lower temperature threshold



DHT dht(DHTPIN, DHTTYPE);

void setup() {
 randomSeed(analogRead(0));

  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  wifiConnect();

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println(WiFi.macAddress());
  stMac = WiFi.macAddress();
  stMac.replace(":", "_");
  Serial.println(stMac);
  
  client.setServer(mqttServer, port);
  client.setCallback(callback);

  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(Relay_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(buzzer, OUTPUT);
  dht.begin();
}

void wifiConnect() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void mqttReconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    long r = random(1000);
    sprintf(clientId, "clientId-%ld", r);
    if (client.connect(clientId)) {
      Serial.print(clientId);
      Serial.println(" connected");
      client.subscribe("topicactivaterelay");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String stMessage;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    stMessage += (char)message[i];
  }
  Serial.println();

  if (String(topic) == "topicactivaterelay") {
    Serial.print("Changing output to ");
    if(stMessage == "on"){
      Serial.println("on");
      digitalWrite(Relay_PIN, HIGH);
      client.publish("STATRELAY", "LED is ON");
    }
    else if(stMessage == "off"){
      Serial.println("off");
      digitalWrite(Relay_PIN, LOW);
      client.publish("STATRELAY", "LED is OFF");
    }
  }
}


void loop() {
  if (!client.connected()) {
    mqttReconnect();
  }
  client.loop();

  int motion = digitalRead(PIR_PIN);
  int lightValue =analogRead(LDR_PIN);
  Serial.println(motion);
 
  if (motion == HIGH){
    client.publish("myproject/motion", "Motion is detected");
  }
  else{
    client.publish("myproject/motion", "Motion is not detected");
  }

  char tempString[8];
  char lumString[8];     
  float t = dht.readTemperature();
  dtostrf(t, 1, 2, tempString);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("°C "));
  client.publish("myproject/temperature", tempString);
  Serial.print("Luminosite: ");
  Serial.println(lightValue);
  dtostrf(lightValue, 1, 2, lumString);
  client.publish("myproject/lumiere", lumString);
  delay(5000);

if ((motion == HIGH)|| (t < TEMP_LOWER_THRESHOLD) || (lightValue > 1300) ){
    digitalWrite(Relay_PIN, HIGH);
    tone(buzzer,600);

  } else 
  { digitalWrite(Relay_PIN, LOW);
    noTone(buzzer);
  }
 
  // il fait nuit et il ya un mouvement 
  /*if (lightValue > 1300 && motion == HIGH ) {
    digitalWrite(Relay_PIN, HIGH);
  } */
  

  
}