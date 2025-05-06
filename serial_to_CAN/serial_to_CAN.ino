#include <SPI.h>
#include "mcp_can.h"

#define CAN_CS_PIN 10
MCP_CAN CAN(CAN_CS_PIN);

String inputString = "";
bool motorEnabled = false;
float position = 0.0f;
String direction = "CW";
float speed = 0.0f;
float min_angle = 0.0f;
float max_angle = 0.0f;
int cycle_count = 0;

// CAN ID for actuator
const int actuator_id = 0x01;  

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (CAN.begin(MCP_ANY, CAN_1000KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("CAN BUS: Initialized");
  } else {
    Serial.println("CAN BUS: Initialization Failed");
    while (1);
  }

  CAN.setMode(MCP_NORMAL);
  delay(100);
  Serial.println("Setup complete.");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(inputString);
      inputString = "";
    } else {
      inputString += c;
    }
  }
}

void processCommand(String cmd) {
  cmd.trim();
  Serial.println("Received: " + cmd);

  if (cmd == "RUN") {
    motorEnabled = true;
    sendCANCommand();
  } else if (cmd == "STOP") {
    motorEnabled = false;
    sendZeroTorque();
  } else if (cmd.startsWith("DIR:")) {
    direction = cmd.substring(4);
  } else if (cmd.startsWith("SPD:")) {
    speed = cmd.substring(4).toFloat();
  } else if (cmd.startsWith("ANG:")) {
    int commaIndex = cmd.indexOf(',');
    if (commaIndex != -1) {
      min_angle = cmd.substring(4, commaIndex).toFloat();
      max_angle = cmd.substring(commaIndex + 1).toFloat();
    }
  } else if (cmd.startsWith("CYC:")) {
    cycle_count = cmd.substring(4).toInt();
  } else if (cmd == "HOME") {
    position = 0.0f;
    sendCANCommand();
  }
}

void sendCANCommand() {
  if (!motorEnabled) return;

  // Determine position increment
  if (direction == "CW") {
    position += 0.1;
    if (position > max_angle) position = min_angle;
  } else {
    position -= 0.1;
    if (position < min_angle) position = max_angle;
  }

  // Dummy values for velocity and gains
  float v_in = 0.0f;
  float kp_in = 20.0f;
  float kd_in = 1.0f;
  float t_in = 0.0f;

  byte buf[8];
  encode_cmd(buf, position, v_in, kp_in, kd_in, t_in);
  CAN.sendMsgBuf(actuator_id, 0, 8, buf);
  Serial.println("Sent CAN cmd to pos: " + String(position, 2));
}

void sendZeroTorque() {
  byte buf[8];
  encode_cmd(buf, 0, 0, 0, 0, 0);
  CAN.sendMsgBuf(actuator_id, 0, 8, buf);
  Serial.println("Sent zero torque.");
}

void encode_cmd(uint8_t* buf, float p, float v, float kp, float kd, float t) {
  int p_int = float_to_uint(p, -12.5f, 12.5f, 16);
  int v_int = float_to_uint(v, -45.0f, 45.0f, 12);
  int kp_int = float_to_uint(kp, 0.0f, 500.0f, 12);
  int kd_int = float_to_uint(kd, 0.0f, 5.0f, 12);
  int t_int = float_to_uint(t, -18.0f, 18.0f, 12);

  buf[0] = (p_int >> 8) & 0xFF;
  buf[1] = p_int & 0xFF;
  buf[2] = (v_int >> 4) & 0xFF;
  buf[3] = ((v_int & 0xF) << 4) | ((kp_int >> 8) & 0xF);
  buf[4] = kp_int & 0xFF;
  buf[5] = (kd_int >> 4) & 0xFF;
  buf[6] = ((kd_int & 0xF) << 4) | ((t_int >> 8) & 0xF);
  buf[7] = t_int & 0xFF;
}

int float_to_uint(float x, float x_min, float x_max, int bits) {
  float span = x_max - x_min;
  float offset = x - x_min;
  return (int)((offset * ((1 << bits) - 1)) / span);
}
