// MAC adress sender: 2c:bc:bb:0e:26:1c
// MAC adress receiver: 1c:69:20:cc:e7:f0


#include <WiFi.h>
#include <esp_now.h>

uint8_t receiverMac[] = {0x1c, 0x69, 0x20, 0xcc, 0xe7, 0xf0};
#define boven_knop 26
#define onder_knop 25


void setup() {
  Serial.begin(9600); 


  pinMode(boven_knop, INPUT_PULLUP);
  pinMode(onder_knop, INPUT_PULLUP);

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init mislukt");
    return;
  }

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverMac, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Peer toevoegen mislukt");
    return;
  }

  Serial.println("ESP-NOW Controller klaar");
}

void loop() {
  int action = 0; // Default action: no movement (0)

  if (digitalRead(boven_knop) == LOW) { // Button is pressed
    action = 1; // omhoog
  } else if (digitalRead(onder_knop) == LOW) { // Button is pressed
    action = -1; // omlaag
  }

  // Send the current action value
  esp_err_t result = esp_now_send(receiverMac, (uint8_t*)&action, sizeof(action));


  delay(100); // debounce + send rate control
}