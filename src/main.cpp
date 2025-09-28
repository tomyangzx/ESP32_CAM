#include "esp_camera.h"
#include <WiFi.h>

// Replace with your network credentials
const char* ssid = "Xiaomi_F71C";
const char* password = "PPqc2qSh!";

void startCameraServer();

void setup() {
	Serial.begin(115200);
	WiFi.begin(ssid, password);
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.print(".");
	}
	Serial.println("");
	Serial.println("WiFi connected");
	Serial.println(WiFi.localIP());

	camera_config_t config;
	config.ledc_channel = LEDC_CHANNEL_0;
	config.ledc_timer = LEDC_TIMER_0;
	config.pin_d0 = 17;
	config.pin_d1 = 35;
	config.pin_d2 = 34;
	config.pin_d3 = 5;
	config.pin_d4 = 39;
	config.pin_d5 = 18;
	config.pin_d6 = 36;
	config.pin_d7 = 19;
	config.pin_xclk = 0;
	config.pin_pclk = 21;
	config.pin_vsync = 25;
	config.pin_href = 23;
	config.pin_sscb_sda = 26;
	config.pin_sscb_scl = 27;
	config.pin_pwdn = 32;
	config.pin_reset = -1;
	config.xclk_freq_hz = 20000000;
	config.pixel_format = PIXFORMAT_JPEG;

	// Init with high specs to pre-allocate larger buffers
	if(psramFound()){
		config.frame_size = FRAMESIZE_UXGA;
		config.jpeg_quality = 10;
		config.fb_count = 2;
	} else {
		config.frame_size = FRAMESIZE_SVGA;
		config.jpeg_quality = 12;
		config.fb_count = 1;
	}

	// Camera init
	esp_err_t err = esp_camera_init(&config);
	if (err != ESP_OK) {
		Serial.printf("Camera init failed with error 0x%x", err);
		return;
	}

	startCameraServer();
	Serial.println("Camera Stream Ready. Go to:");
	Serial.print("http://");
	Serial.println(WiFi.localIP());
}

void loop() {
	delay(10000);
}

// Dummy camera server function
void startCameraServer() {
	// In a real project, use the ESP32 CameraWebServer library
}