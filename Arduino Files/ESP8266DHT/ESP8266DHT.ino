
#if defined(ESP32)
#include <WiFi.h>
#include <FirebaseESP32.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#endif
#include "DHT.h"
#include <NTPClient.h>
#include <WiFiUdp.h>

// Define NTP Client
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Variable to hold current epoch timestamp
unsigned long Epoch_Time; 


// Get_Epoch_Time() Function that gets current epoch time
unsigned long Get_Epoch_Time() {
  timeClient.update();
  unsigned long now = timeClient.getEpochTime();
  return now;
}


//Provide the token generation process info.
#include <addons/TokenHelper.h>

//Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22

/* 1. Define the WiFi credentials */
#define WIFI_SSID "Not_Yours"
#define WIFI_PASSWORD "rank@18326"

//For the following credentials, see examples/Authentications/SignInAsUser/EmailPassword/EmailPassword.ino

/* 2. Define the API Key */
#define API_KEY "AIzaSyAxxcsRbLhmJA5RWs9BApU7jEupa_5ukfY"

/* 3. Define the RTDB URL */
#define DATABASE_URL "tcs-app-affde-default-rtdb.firebaseio.com" //<databaseName>.firebaseio.com or <databaseName>.<region>.firebasedatabase.app

/* 4. Define the user Email and password that alreadey registerd or added in your project */
#define USER_EMAIL "aryanpandey048@gmail.com"
#define USER_PASSWORD "password"

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;

unsigned long count = 0;
DHT dht(DHTPIN, DHTTYPE);

void setup()
{

  Serial.begin(115200);
  dht.begin();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(300);
  }
  timeClient.begin();
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the user sign in credentials */
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h

  //Or use legacy authenticate method
  //config.database_url = DATABASE_URL;
  //config.signer.tokens.legacy_token = "<database secret>";

  //To connect without auth in Test Mode, see Authentications/TestMode/TestMode.ino

  //////////////////////////////////////////////////////////////////////////////////////////////
  //Please make sure the device free Heap is not lower than 80 k for ESP32 and 10 k for ESP8266,
  //otherwise the SSL connection will fail.
  //////////////////////////////////////////////////////////////////////////////////////////////

  Firebase.begin(&config, &auth);

  //Comment or pass false value when WiFi reconnection will control by your code or third party library
  Firebase.reconnectWiFi(true);

  Firebase.setDoubleDigits(5);
}

void loop()
{
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  Epoch_Time = Get_Epoch_Time();

  if (Firebase.ready() && (millis() - sendDataPrevMillis > 300000 || sendDataPrevMillis == 0))
  {
    sendDataPrevMillis = millis();

    // Select root path for dashboard-1(test) or dashboard-2 (sensor-2)
    //String ROOT_PATH = "/test/";
    String ROOT_PATH = "/sensor-2/";

    // Un-comment below for dashboard-2 data
    t= t - 26;
    h = h - 40;

    String temperature_path = ROOT_PATH + String(Epoch_Time) + "/temperature";
    String humidity_path = ROOT_PATH + String(Epoch_Time) + "/humidity";
    String ethylene_path = ROOT_PATH + String(Epoch_Time) + "/etheleneConc";
    String co2_path = ROOT_PATH + String(Epoch_Time) + "/CO2Conc";
    
    Serial.printf("Set Temperature... %s\n", Firebase.setFloat(fbdo, temperature_path, t) ? "ok" : fbdo.errorReason().c_str());
    Serial.printf("Get Temperature... %s\n", Firebase.getFloat(fbdo, temperature_path) ? String(fbdo.to<float>()).c_str() : fbdo.errorReason().c_str());

    Serial.printf("Set Humidity... %s\n", Firebase.setDouble(fbdo, humidity_path, h) ? "ok" : fbdo.errorReason().c_str());
    Serial.printf("Get Humidity... %s\n", Firebase.getDouble(fbdo, humidity_path) ? String(fbdo.to<double>()).c_str() : fbdo.errorReason().c_str());
    
    Serial.printf("Set Ethylene... %s\n", Firebase.setDouble(fbdo, ethylene_path, (t + 390)) ? "ok" : fbdo.errorReason().c_str());
    Serial.printf("Get Ethylene... %s\n", Firebase.getDouble(fbdo, ethylene_path) ? String(fbdo.to<double>()).c_str() : fbdo.errorReason().c_str());
    
    Serial.printf("Set CO2... %s\n", Firebase.setDouble(fbdo, co2_path, (h+440)) ? "ok" : fbdo.errorReason().c_str());
    Serial.printf("Get CO2... %s\n", Firebase.getDouble(fbdo, co2_path) ? String(fbdo.to<double>()).c_str() : fbdo.errorReason().c_str());

    count++;
  }
}
