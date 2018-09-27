#include <Arduino_FreeRTOS.h>

#include <Arduino.h>
#include <avr/io.h>

#include <SoftwareSerial.h>

#include <task.h>
#include <semphr.h>
#include <timers.h>

#define STACK_SIZE 200
#define BUFFER_SIZE 250
#define FALSE 0
#define TRUE 1

typedef struct {
  int sensorID;
  int x_value; int y_value; int z_value;
} AccelPacket;

typedef struct {
  int sensorID;
  int x_value; int y_value; int z_value;
  int g_x_value; int g_y_value; int g_z_value;
} IMUPacket;

typedef struct {
  AccelPacket leftHand;
  AccelPacket rightHand;
  AccelPacket leftKnee;
  AccelPacket rightKnee;
  IMUPacket torso;
} SensorPacket;

/*----------Function Prototype------------*/

void initialise_handshake();
void read_power();
void read_sensor();
void send_reading();
void send_reading_serial();
void serialise(int);
void createMessage();
void testUART();
SoftwareSerial mySerial(10,11); // RX, TX for uno use

/*------------Global Variable-------------*/

SensorPacket sp;

// Handshaking variables
int handshake_done = 0;
int ack_flag = 0;

// Send reading variables
char response = 0;

int header_id = 0;
int ack_received = 1; // Set to 1 for the 1st round
boolean new_data = FALSE;

// Buffer variables
char buffer[BUFFER_SIZE];
int len = 0;

// Read power variables
int voltage;
int current;

// Creating string variables
char leftHand_id[4], leftHand_x[4], leftHand_y[4], leftHand_z[4];
char leftKnee_id[4], leftKnee_x[4], leftKnee_y[4], leftKnee_z[4];
char rightHand_id[4], rightHand_x[4], rightHand_y[4], rightHand_z[4];
char rightKnee_id[4], rightKnee_x[4], rightKnee_y[4], rightKnee_z[4];
char torso_id[4], torso_x[4], torso_y[4], torso_z[4];
char torso_g_x[4], torso_g_y[4], torso_g_z[4];

char volt[4], curr[4];
char checksumChar[4];
char headID[4];



void read_sensor(void *p) {
  TickType_t rsLastWakeTime;
  const TickType_t rsFrequency = 300;
  rsLastWakeTime = xTaskGetTickCount();

  while(1) {
    // dummy values inserted
    Serial.println("------READ SENSORS FUNC------");
    // getting values depending on the uptime
    // sp.leftHand.x_value = 0;// * millis()/1000;
    // sp.leftHand.y_value = 1;// * millis()/1000;
    // sp.leftHand.z_value = 2;// * millis()/1000;
    //
    // sp.rightHand.x_value = 3;// * millis()/1000;
    // sp.rightHand.y_value = 4;// * millis()/1000;
    // sp.rightHand.z_value = 5;// * millis()/1000;
    //
    // sp.leftKnee.x_value = -1;// * millis()/1000;
    // sp.leftKnee.y_value = -2;// * millis()/1000;
    // sp.leftKnee.z_value = -3;// * millis()/1000;
    //
    // sp.rightKnee.x_value = 6;// * millis()/1000;
    // sp.rightKnee.y_value = 7;// * millis()/1000;
    // sp.rightKnee.z_value = 8;// * millis()/1000;
    //
    // sp.torso.x_value = 9;// * millis()/1000;
    // sp.torso.y_value = 10;// * millis()/1000;
    // sp.torso.z_value = 11;// * millis()/1000;
    // sp.torso.g_x_value = 123;// * millis()/1000;
    // sp.torso.g_y_value = -456;// * millis()/1000;
    // sp.torso.g_z_value = 7890;// * millis()/1000;

    read_power();

    new_data = TRUE;
    // testUART();
    /*
        overflow and establish contact again
    */
    serialise(header_id++);
    send_reading_serial();
    // Delay for 5ms, sampling rate = 200Hz
    vTaskDelayUntil(&rsLastWakeTime, rsFrequency);
  }
}

void read_power() {
  Serial.println("Reading power value...");
  voltage = 12;
  current = 34;
}

void send_reading_serial() {
  Serial.println("Sending serial over...");
  Serial.println(buffer);
  for(int i=0; i<len+2; i++) {
    mySerial.write(buffer[i]); // mySerial write
  }
  strcpy(buffer, ""); // to be removed
}

void serialise(int id) {
  char checksum = 0;

  // Append header ID to buffer
  itoa(id, headID, 10);
  strcat(buffer, headID);
  strcat(buffer, ",");

  createMessage();

  len = strlen(buffer);
  for(int i=0; i<len-1; i++) {
    checksum ^= buffer[i];
    Serial.print("buffer[i] = \'");
    Serial.print(buffer[i]);
    Serial.print("\', checksum = \'");
    Serial.print(checksum);
    Serial.println("\'");
  }
  // Append checksum to buffer
  itoa(checksum, checksumChar, 10);
  strcat(buffer, checksumChar);
  strcat(buffer, ",");
  // buffer[len] = checksum;
  Serial.print("Checksum = ");
  Serial.println(checksum);

  len = strlen(buffer);
  Serial.print("Last in buffer is ");
  Serial.print(buffer[len]);
  Serial.println();
  buffer[len+1] = '\n'; // append \n to back of string
}

void createMessage() {
  Serial.println("Creating string~~~");
  // Converting int to characters

  // // leftHand
  // itoa(sp.leftHand.sensorID, leftHand_id, 10);
  // strcat(buffer, leftHand_id, 10);
  // strcat(buffer, ",");
  // itoa(sp.leftHand.x_value, leftHand_x, 10);  // 10 is base
  // strcat(buffer, leftHand_x);
  // strcat(buffer, ",");
  // itoa(sp.leftHand.y_value, leftHand_y, 10);  // 10 is base
  // strcat(buffer, leftHand_y);
  // strcat(buffer, ",");
  // itoa(sp.leftHand.z_value, leftHand_z, 10);  // 10 is base
  // strcat(buffer, leftHand_z);
  // strcat(buffer, ",");
  //
  // // rightHand
  // itoa(sp.rightHand.sensorID, rightHand_id, 10);
  // strcat(buffer, rightHand_id, 10);
  // strcat(buffer, ",");
  // itoa(sp.rightHand.x_value, rightHand_x, 10);  // 10 is base
  // strcat(buffer, rightHand_x);
  // strcat(buffer, ",");
  // itoa(sp.rightHand.y_value, rightHand_y, 10);  // 10 is base
  // strcat(buffer, rightHand_y);
  // strcat(buffer, ",");
  // itoa(sp.rightHand.z_value, rightHand_z, 10);  // 10 is base
  // strcat(buffer, rightHand_z);
  // strcat(buffer, ",");
  //
  // // leftKnee
  // itoa(sp.leftKnee.sensorID, leftKnee_id, 10);
  // strcat(buffer, leftKnee_id, 10);
  // strcat(buffer, ",");
  // itoa(sp.leftKnee.x_value, leftKnee_x, 10);  // 10 is base
  // strcat(buffer, leftKnee_x);
  // strcat(buffer, ",");
  // itoa(sp.leftKnee.y_value, leftKnee_y, 10);  // 10 is base
  // strcat(buffer, leftKnee_y);
  // strcat(buffer, ",");
  // itoa(sp.leftKnee.z_value, leftKnee_z, 10);  // 10 is base
  // strcat(buffer, leftKnee_z);
  // strcat(buffer, ",");
  //
  // // rightKnee
  // itoa(sp.rightKnee.sensorID, rightKnee_id, 10);
  // strcat(buffer, rightKnee_id, 10);
  // strcat(buffer, ",");
  // itoa(sp.rightKnee.x_value, rightKnee_x, 10);  // 10 is base
  // strcat(buffer, rightKnee_x);
  // strcat(buffer, ",");
  // itoa(sp.rightKnee.y_value, rightKnee_y, 10);  // 10 is base
  // strcat(buffer, rightKnee_y);
  // strcat(buffer, ",");
  // itoa(sp.rightKnee.z_value, rightKnee_z, 10);  // 10 is base
  // strcat(buffer, rightKnee_z);
  // strcat(buffer, ",");
  //
  // // torso
  // itoa(sp.torso.sensorID, torso_id, 10);
  // strcat(buffer, torso_id, 10);
  // strcat(buffer, ",");
  // itoa(sp.torso.x_value, torso_x, 10);  // 10 is base
  // strcat(buffer, torso_x);
  // strcat(buffer, ",");
  // itoa(sp.torso.y_value, torso_y, 10);  // 10 is base
  // strcat(buffer, torso_y);
  // strcat(buffer, ",");
  // itoa(sp.torso.z_value, torso_z, 10);  // 10 is base
  // strcat(buffer, torso_z);
  // strcat(buffer, ",");
  // itoa(sp.torso.g_x_value, torso_g_x, 10);  // 10 is base
  // strcat(buffer, torso_g_x);
  // strcat(buffer, ",");
  // itoa(sp.torso.g_y_value, torso_g_y, 10);  // 10 is base
  // strcat(buffer, torso_g_y);
  // strcat(buffer, ",");
  // itoa(sp.torso.g_z_value, torso_g_z, 10);  // 10 is base
  // strcat(buffer, torso_g_z);
  // strcat(buffer, ",");

  // Power reading
  itoa(voltage, volt, 10);
  strcat(buffer, volt);
  strcat(buffer, ",");
  itoa(current, curr, 10);
  strcat(buffer, curr);
  strcat(buffer, ",");
}

void send_reading(void *p) {
  // TickType_t srLastWakeTime;
  // const TickType_t srFrequency = 200;
  // srLastWakeTime = xTaskGetTickCount();
  // Serial.println("Enter SR");
  while (1) {
    // Serial.println("------SEND READING FUNC------");

    if (Serial.available()) {
      Serial.println("debug2");
    }

    // if (mySerial.available()) {
    //   response = mySerial.read();
    // }
    //
    // if (response == 'A') {
    //   Serial.println("Acknowledgment received from rPi");
    //   strcpy(buffer, "");
    //   ack_received = 1;
    //   response = 0;
    // } else if (response == 'N') {
    //   Serial.println("Resending previous buffer...");
    //   send_reading_serial();
    //   response = 0;
    // } else if (response == 'H'){
    //   header_id = 0;
    //   handshake_done = 0;
    //   ack_flag = 0;
    //   response = 0;
    //   Serial.println("Request for handshake...");
    //   initialise_handshake();
    // } else {
    //   response = 0;
    //   Serial.print(new_data);
    //   Serial.print(" ");
    //   Serial.println(ack_received);
    // }
    //
    // if (new_data && ack_received) {
    //   serialise(header_id++);
    //   send_reading_serial();
    //   new_data = FALSE;
    //   ack_received = 0;
    // }

    // vTaskDelayUntil(&srLastWakeTime, srFrequency);
  }
}

void initialise_handshake(void) {
  while(!handshake_done) {
    if(mySerial.available()) {
      // Serial.println("Inside");
      char readByte = mySerial.read();
      if(readByte == 'H') {
        mySerial.write('A');
        ack_flag = 1;
        Serial.println("Received Hello from Pi.");
      } else if((readByte == 'A')&&(ack_flag == 1)) {
        handshake_done = 1;
        Serial.println("Handshaking done! Sweaty palms~");
      } else {
        Serial.print(readByte);
        Serial.println(" : wrong byte..");
        // mySerial.write('R');
      }
    }
  }
}

void testUART() {
  strcpy(buffer, "");

  int val = 4545;
  int val2 = 1212;
  char valc[4], val2c[4];

  itoa(val, valc, 10);
  strcat(buffer, valc);
  strcat(buffer, ",");
  itoa(val2, val2c, 10);
  strcat(buffer, val2c);
  strcat(buffer, ",");

  len = strlen(buffer);
  Serial.print("Last in buffer is");
  Serial.print(buffer[len]);
  Serial.println();
  buffer[len+1] = '\n';

  Serial.println(buffer);
  for(int i=0; i<len+2; i++) {
    mySerial.write(buffer[i]);
  }
}

void setup() {
  sp.torso.sensorID = 0;
  sp.leftHand.sensorID = 1;
  sp.rightHand.sensorID = 2;
  sp.leftKnee.sensorID = 3;
  sp.rightKnee.sensorID = 4;

  Serial.begin(115200);
  mySerial.begin(115200); // To be changed when using Mega

  Serial.println("Arduino Powering up....");

  /* to be implemented with actual pi */
  Serial.println("Initialising handshake protocol...");
  initialise_handshake();

  xTaskCreate(read_sensor, "Reading Sensor", STACK_SIZE, NULL, 1, NULL);
  // xTaskCreate(send_reading, "Sending Reading", STACK_SIZE, NULL, 2, NULL);
  // Serial.println("Start scheduler");
  vTaskStartScheduler();
  Serial.println("Debug");
}

void loop() {

}
