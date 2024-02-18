#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h" 

#define PIR_PIN 13 
#define Relay_PIN 4
#define LDR_PIN 34
#define buzzer 18
#define DHTPIN 15
#define DHTTYPE DHT22 
#define TEMP_UPPER_THRESHOLD  25 // upper temperature threshold
#define TEMP_LOWER_THRESHOLD  22 // lower temperature threshold


const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqttServer = "broker.hivemq.com";
int port = 1883;
String stMac;
char mac[50];
char clientId[50];

WiFiClient espClient;
PubSubClient client(espClient);
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
      tone(buzzer,600);
      client.publish("STATRELAY", "Intrusion system is Activated");
    }
    else if(stMessage == "off"){
      Serial.println("off");
      digitalWrite(Relay_PIN, LOW);
      noTone(buzzer);
      client.publish("STATRELAY", "Intrusion system is Deactivated");
    }
  }
}


void loop() {
  if (!client.connected()) {
    mqttReconnect();
  }
  client.loop();

/****** Aquisition des données des capteurs ******/
  int motion = digitalRead(PIR_PIN);  //capteur de mouvemnt
  int lightValue =analogRead(LDR_PIN); //capteur de lumiére 
  float t = dht.readTemperature(); // capteur de température 
  


/****** Pubblier les mesures des trois capteurs *******/
  char tempString[8];
  char lumString[8];     
  dtostrf(t, 1, 2, tempString);
  client.publish("myproject/temperature", tempString);
  dtostrf(lightValue, 1, 2, lumString);
  client.publish("myproject/lumiere", lumString);
  if (motion == HIGH){
    client.publish("myproject/motion", "Motion is detected");
  }
  else{
    client.publish("myproject/motion", "Motion is not detected");
  }

/****** Affichage des mesures des capteurs *******/
  Serial.println(motion);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("°C "));
  Serial.print("Luminosite: ");
  Serial.println(lightValue);
  delay(5000);


/****** Les Conditions d'activation du systéme ******/
char ledState[8];
if ((motion == HIGH)|| (t < TEMP_LOWER_THRESHOLD) ){  // il y a un mouvement ou il y a un abaissement brusque de température 
    digitalWrite(Relay_PIN, HIGH);
    tone(buzzer,600);
    client.publish("myproject/intrusion", "Alert!! Someone is is detected");
}  
else if ((motion == HIGH) && (lightValue > 1300)){  // il fait nuit et il ya un mouvement
    digitalWrite(Relay_PIN, HIGH);
    tone(buzzer,600);
    client.publish("myproject/intrusion", "Alert!! Someone is is detected");
}
else 
  { digitalWrite(Relay_PIN, LOW);
    noTone(buzzer);
  }
 
   
 
  

  
}