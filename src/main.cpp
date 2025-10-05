/*******#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h" //disable brownout problems
#include "soc/rtc_cntl_reg.h"  //disable brownout problems
#include "esp_http_server.h"
#include "wifi_config.h"  // Local WiFi configurationd ESP32-CAM Video Streaming Server
  Optimized for OpenCV compatibility
  
  Based on: RandomNerdTutorials.com ESP32-CAM streaming example
  Enhanced for better OpenCV integration and stability
*********/

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h" //disable brownout problems
#include "soc/rtc_cntl_reg.h"  //disable brownout problems
#include "esp_http_server.h"
#include "wifi_config.h"  // Local WiFi configuration

// Device identifier (change for second device)
const char* device_name = "ESP32_CAM_1";  // Change to "ESP32_CAM_2" for second device

#define PART_BOUNDARY "123456789000000000000987654321"

// Camera model selection
#define CAMERA_MODEL_AI_THINKER
//#define CAMERA_MODEL_M5STACK_PSRAM
//#define CAMERA_MODEL_M5STACK_WITHOUT_PSRAM

#if defined(CAMERA_MODEL_AI_THINKER)
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#else
  #error "Camera model not selected"
#endif

static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

// Enhanced stream handler with better OpenCV compatibility
static esp_err_t stream_handler(httpd_req_t *req){
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[128];
  
  Serial.println("Stream client connected");

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if(res != ESP_OK){
    return res;
  }

  // Add CORS headers for better compatibility
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
  
  uint32_t frame_count = 0;
  unsigned long last_frame_time = millis();
  
  while(true){
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      res = ESP_FAIL;
      break;
    } else {
      frame_count++;
      
      // Process all frames, not just width > 400
      if(fb->format != PIXFORMAT_JPEG){
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if(!jpeg_converted){
          Serial.println("JPEG compression failed");
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    
    if(res == ESP_OK){
      size_t hlen = snprintf((char *)part_buf, 128, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }
    
    if(fb){
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if(_jpg_buf){
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    
    if(res != ESP_OK){
      Serial.println("Stream client disconnected");
      break;
    }
    
    // Log frame rate every 100 frames
    if(frame_count % 100 == 0) {
      unsigned long current_time = millis();
      float fps = 100000.0 / (current_time - last_frame_time);
      Serial.printf("Frames: %u, FPS: %.1f\n", frame_count, fps);
      last_frame_time = current_time;
    }
    
    // Small delay to prevent overwhelming the client
    delay(33); // ~30 FPS max
  }
  
  return res;
}

// Simple status page handler
static esp_err_t index_handler(httpd_req_t *req){
  char html_page[2048];
  
  snprintf(html_page, sizeof(html_page),
    "<!DOCTYPE html>\n"
    "<html><head><title>%s</title></head>\n"
    "<body style='font-family: Arial;'>\n"
    "<h2>%s Status</h2>\n"
    "<p><strong>IP Address:</strong> %s</p>\n"
    "<p><strong>MAC Address:</strong> %s</p>\n"
    "<p><strong>Free Heap:</strong> %u bytes</p>\n"
    "<p><strong>Uptime:</strong> %lu seconds</p>\n"
    "<hr>\n"
    "<h3>Stream URLs:</h3>\n"
    "<p><a href='/stream'>MJPEG Stream</a> (for OpenCV)</p>\n"
    "<p><a href='/'>This page</a></p>\n"
    "<hr>\n"
    "<h3>Live Preview:</h3>\n"
    "<img src='/stream' style='max-width: 640px; border: 1px solid #ccc;'>\n"
    "</body></html>",
    device_name, device_name, 
    WiFi.localIP().toString().c_str(),
    WiFi.macAddress().c_str(),
    ESP.getFreeHeap(),
    millis() / 1000
  );
  
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, html_page, strlen(html_page));
}

void startCameraServer(){
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.max_uri_handlers = 10;
  config.task_priority = 6;
  config.stack_size = 8192;

  // Main status page
  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };
  
  // Stream endpoint
  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };
  
  Serial.printf("Starting web server on port: %d\n", config.server_port);
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &index_uri);
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    Serial.println("HTTP server started successfully");
  } else {
    Serial.println("Failed to start HTTP server");
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
 
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println("\n=== ESP32-CAM Enhanced Streaming Server ===");
  Serial.printf("Device: %s\n", device_name);
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; 
  
  // Enhanced camera settings for OpenCV compatibility
  if(psramFound()){
    Serial.println("PSRAM found - using high resolution");
    config.frame_size = FRAMESIZE_SVGA;  // 800x600 - good balance
    config.jpeg_quality = 12;            // Good quality
    config.fb_count = 2;                 // Double buffering
  } else {
    Serial.println("No PSRAM - using standard resolution");
    config.frame_size = FRAMESIZE_VGA;   // 640x480
    config.jpeg_quality = 15;            // Lower quality for no PSRAM
    config.fb_count = 1;
  }
  
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }
  
  Serial.println("Camera initialized successfully");
  
  // Get camera sensor for additional settings
  sensor_t * s = esp_camera_sensor_get();
  if (s) {
    // Optimize settings for streaming
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0 to 6 (0-No Effect, 1-Negative, 2-Grayscale, 3-Red Tint, 4-Green Tint, 5-Blue Tint, 6-Sepia)
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    s->set_aec2(s, 0);           // 0 = disable , 1 = enable
    s->set_ae_level(s, 0);       // -2 to 2
    s->set_aec_value(s, 300);    // 0 to 1200
    s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
    s->set_bpc(s, 0);            // 0 = disable , 1 = enable
    s->set_wpc(s, 1);            // 0 = disable , 1 = enable
    s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
    s->set_lenc(s, 1);           // 0 = disable , 1 = enable
    s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
    s->set_vflip(s, 0);          // 0 = disable , 1 = enable
    s->set_dcw(s, 1);            // 0 = disable , 1 = enable
    s->set_colorbar(s, 0);       // 0 = disable , 1 = enable
    
    Serial.println("Camera sensor configured");
  }
  
  // Wi-Fi connection
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  Serial.printf(" (%s)", WIFI_SSID);
  
  int wifi_attempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifi_attempts < 30) {
    delay(500);
    Serial.print(".");
    wifi_attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected successfully!");
    Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("MAC address: %s\n", WiFi.macAddress().c_str());
    
    // Start streaming web server
    startCameraServer();
    
    Serial.println("\n=== Camera Server Ready ===");
    Serial.printf("Status page: http://%s/\n", WiFi.localIP().toString().c_str());
    Serial.printf("Stream URL:  http://%s/stream\n", WiFi.localIP().toString().c_str());
    Serial.printf("For OpenCV:  http://%s/\n", WiFi.localIP().toString().c_str());
    Serial.println("===============================");
    
  } else {
    Serial.println("\nFailed to connect to WiFi!");
    Serial.println("Please check credentials and try again.");
  }
}

void loop() {
  delay(100);
  
  // Print periodic status
  static unsigned long last_status = 0;
  if (millis() - last_status > 60000) {  // Every minute
    Serial.printf("Uptime: %lu seconds, Free heap: %u bytes\n", 
                  millis() / 1000, ESP.getFreeHeap());
    last_status = millis();
  }
}