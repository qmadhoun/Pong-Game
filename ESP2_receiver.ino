// MAC adress sender: 2c:bc:bb:0e:26:1c
// MAC adress receiver: 1c:69:20:cc:e7:f0


#include <WiFi.h>
#include <esp_now.h>
#include <ArduinoMqttClient.h>

// --- WIFI & MQTT Config ---
const char* ssid = "E109-E110";
const char* password = "DBHaacht24";
const char* broker = "192.168.0.157";

// --- MQTT Setup ---
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// --- Vertrouwd MAC-adres van sender
uint8_t trustedSender[] = {0x2c, 0xbc, 0xbb, 0x0e, 0x26, 0x1c};

// CORRECTED FUNCTION SIGNATURE
void onDataReceive(const esp_now_recv_info_t *recv_info, const uint8_t *incomingData, int len) {
  // Check of het bericht van de vertrouwde zender komt
  // CORRECTED: use recv_info->src_addr instead of mac
  if (memcmp(recv_info->src_addr, trustedSender, 6) != 0) {
    Serial.println("Ongeloofwaardige zender! Bericht genegeerd.");
    return;
  }

  int action;
  memcpy(&action, incomingData, sizeof(action));

  Serial.print("Actie ontvangen van vertrouwde zender: ");
  Serial.println(action);

  if (!mqttClient.connected()) {
    Serial.println("MQTT niet verbonden, opnieuw verbinden...");
    mqttClient.connect(broker, 1883);
  }

  mqttClient.beginMessage("pong/control");
  mqttClient.print(action);
  mqttClient.endMessage();
}

void setup() {
  Serial.begin(9600);

  // Connect met WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Verbinden met WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nWiFi verbonden");

  // MQTT client setup
  mqttClient.setId("esp32-receiver");
  if (mqttClient.connect(broker, 1883)) {
    Serial.println("MQTT verbonden");
  } else {
    Serial.println("MQTT connectie mislukt!");
  }

  // ESP-NOW initialiseren
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init mislukt");
    return;
  }

  // Voeg peer toe — alleen berichten van deze peer accepteren
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, trustedSender, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Toevoegen peer mislukt!");
    return;
  }

  // Registreer callback function om berichten te ontvangen
  esp_now_register_recv_cb(onDataReceive); // 

  Serial.println("ESP-NOW ontvanger klaar, wacht op berichten van vertrouwde zender...");
}

void loop() {
  mqttClient.poll();
}