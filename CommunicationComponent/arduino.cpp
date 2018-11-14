#include <Arduino_FreeRTOS.h>

#include <Arduino.h>
#include <avr/io.h>

#include <task.h>
#include <timers.h>
#include <semphr.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <MPU6050_tockn.h>


#define STACK_SIZE 200
#define BUFFER_SIZE 300
#define FALSE 0
#define TRUE 1
#define TIMEOUT_HANDSHAKE 5000
#define TIMEOUT_EST 1000 // Estimate Timeout from test (141 for FREQ = 10)
#define TIMEOUT_VAR 0.7 // Weight for calculating timeout
#define RSFREQ 2
#define SRFREQ 2

typedef struct {
  int sensorID;
  float x_value; float y_value; float z_value;
} AccelPacket;

typedef struct {
  int sensorID;
  float x_value; float y_value; float z_value;
  float g_x_value; float g_y_value; float g_z_value;
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
void reset_variables(char);
void read_power();
void read_ACC(int);
void read_IMU();
void read_sensor();
void send_reading();
void send_reading_serial();
void serialise(int);
void createMessage();
void testUART();
void accSetup(int);
char *ftoa(char*, double, int);

/*------------Global Variable-------------*/

SensorPacket sp;
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

// Handshaking variables
boolean handshake_done = FALSE;
int ack_flag = 0;
boolean handshake_first = TRUE;

// Send reading variables
char response = 0;
int header_id = 0;
int ack_received = 1; // Set to 1 for the 1st round
boolean new_data = FALSE;

// Timeout Variables
unsigned long currTime, prevTime;
unsigned long RTT_currTime, RTT_prevTime;
unsigned int RTT_TIMEOUT;
unsigned int TIMEOUT_SERIAL;
boolean first_try = TRUE;

// Buffer variables
char buffer[BUFFER_SIZE];
int len = 0;

// Read power variables
float voltage;
float current;
int CURRENT_PIN = A0;  // Input pin for measuring curr
/*
  RS = 0.1;  // Shunt resistor value (in ohms)
  VOLTAGE_REF = 5; // Reference voltage for analog read
  current = (((C_PIN) * VOLTAGE_REF) / 1023) / (10.0 * RS);
*/
int VOLTAGE_PIN = A1;  // Input pin for measuring volt
/*
  R1 = R2 = 82000.0;
  vout = ((V_PIN)*5.0)/1023.0;
  vin = vout * ((R1+R2)/R2);
*/

// Sensors Variables
/* Assign a unique ID to this sensor at the same time */
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
MPU6050 mpu6050(Wire);
int accelNo = 0;
int LHAND_PIN = 38; int RHAND_PIN = 52;
int LKNEE_PIN = 48; int RKNEE_PIN = 42; // LK 48, RK 42

// Creating string variables
char leftHand_id[5], leftHand_x[6], leftHand_y[6], leftHand_z[6];
char leftKnee_id[5], leftKnee_x[6], leftKnee_y[6], leftKnee_z[6];
char rightHand_id[5], rightHand_x[6], rightHand_y[6], rightHand_z[6];
char rightKnee_id[5], rightKnee_x[6], rightKnee_y[6], rightKnee_z[6];
char torso_id[5], torso_x[6], torso_y[6], torso_z[6];
char torso_g_x[6], torso_g_y[6], torso_g_z[6];

char volt[8], curr[8];
char checksumChar[5];
char headID[5];

/*
  purple tx
  yellow rx
  blue   5v
  grey   gnd
*/

/*********************************************************************
                              WARNING
  1. Please add/change these lines containing 'break' to if-else
  2. add self.ser.readline after 	isHandshakeDone = True
  3. add packet = packet.strip('\x00')
        to remove leading and trailing \x00
                              TODO
  1. add timeout in python comms script
      a. for handshake TIMEOUT
      b. for serial data transfer TIMEOUT
      c. for requesting of new handshake
**********************************************************************/


/*-----------------------------------------------------*/
/*>>>>>>>>>>>>>>>READING FUNCTIONS>>>>>>>>>>>>>>>>>>>>>*/
/*-----------------------------------------------------*/
void read_sensor(void *p) {
  const TickType_t rsFrequency = RSFREQ;

  while(1) {

// /*
//   Debugging
// */
// Serial.print("Current time sensor mutex = ");
// Serial.println(millis());

    if (xSemaphoreTake(mutex, (TickType_t) 1000)) {
      // Serial.println("------READ SENSORS FUNC------");

      digitalWrite(LHAND_PIN, LOW);
      digitalWrite(RHAND_PIN, HIGH);
      // digitalWrite(LKNEE_PIN, HIGH);
      // digitalWrite(RKNEE_PIN, HIGH);
      read_ACC(sp.leftHand.sensorID);
      // digitalWrite(LHAND_PIN, HIGH);

      digitalWrite(LHAND_PIN, HIGH);
      digitalWrite(RHAND_PIN, LOW);
      // digitalWrite(LKNEE_PIN, HIGH);
      // digitalWrite(RKNEE_PIN, HIGH);
      read_ACC(sp.rightHand.sensorID);
      // digitalWrite(RHAND_PIN, HIGH);

      // digitalWrite(LHAND_PIN, HIGH);
      // digitalWrite(RHAND_PIN, HIGH);
      // digitalWrite(LKNEE_PIN, LOW);
      // // digitalWrite(RKNEE_PIN, HIGH);
      // read_ACC(sp.leftKnee.sensorID);
      // digitalWrite(LKNEE_PIN, HIGH);
      //
      // digitalWrite(LHAND_PIN, HIGH);
      // digitalWrite(RHAND_PIN, HIGH);
      // digitalWrite(LKNEE_PIN, HIGH);
      // digitalWrite(RKNEE_PIN, LOW);
      // read_ACC(sp.rightKnee.sensorID);
      // digitalWrite(RKNEE_PIN, HIGH);

      read_IMU();
      read_power();

      // Serial.print("LHAND Values: ");
      // Serial.print(sp.leftHand.x_value);
      // Serial.print(" , ");
      // Serial.print(sp.leftHand.y_value);
      // Serial.print(" , ");
      // Serial.println(sp.leftHand.z_value);
      // Serial.print("RHAND Values: ");
      // Serial.print(sp.rightHand.x_value);
      // Serial.print(" , ");
      // Serial.print(sp.rightHand.y_value);
      // Serial.print(" , ");
      // Serial.println(sp.rightHand.z_value);

      new_data = TRUE;
      xSemaphoreGive(mutex);
    }
    /*
        TODO: overflow
    */

// /*
//   Debugging
// */
// Serial.print("Current time end sensor = ");
// Serial.println(millis());

    // Delay for 5ms, sampling rate = 200Hz
    vTaskDelay(rsFrequency);
  }
}

void read_power() {
  // Serial.println("Reading Power ...");
  voltage = analogRead(VOLTAGE_PIN);
  current = analogRead(CURRENT_PIN);
}

void read_IMU() {
  // Serial.println("Reading  IMU  ...");
  mpu6050.update();
  sp.torso.x_value = mpu6050.getAccX();
  sp.torso.y_value = mpu6050.getAccY();
  sp.torso.z_value = mpu6050.getAccZ();
  sp.torso.g_x_value = mpu6050.getGyroX();
  sp.torso.g_y_value = mpu6050.getGyroY();
  sp.torso.g_z_value = mpu6050.getGyroZ();
}

void read_ACC(int accelNo) {
  /*Get a new sensor event */
  sensors_event_t accelEvent;
  accel.getEvent(&accelEvent);

  switch (accelNo) {
    case 0:
      sp.rightHand.x_value = accelEvent.acceleration.x;
      sp.rightHand.y_value = accelEvent.acceleration.y;
      sp.rightHand.z_value = accelEvent.acceleration.z;
      if((sp.rightHand.x_value + sp.rightHand.y_value + sp.rightHand.z_value) == 0) {
        Serial.println("RH sensor broke");
        accSetup(sp.rightHand.sensorID);
      }
      break;
    case 1:
      sp.leftHand.x_value = accelEvent.acceleration.x;
      sp.leftHand.y_value = accelEvent.acceleration.y;
      sp.leftHand.z_value = accelEvent.acceleration.z;
      if((sp.leftHand.x_value + sp.leftHand.y_value + sp.leftHand.z_value) == 0) {
        accSetup(sp.leftHand.sensorID);
        Serial.println("LH sensor broke");
      }
      break;
    case 2:
      sp.rightKnee.x_value = accelEvent.acceleration.x;
      sp.rightKnee.y_value = accelEvent.acceleration.y;
      sp.rightKnee.z_value = accelEvent.acceleration.z;
      if((sp.rightKnee.x_value + sp.rightKnee.y_value + sp.rightKnee.z_value) == 0) {
        accSetup(sp.rightKnee.sensorID);
        Serial.println("RK sensor broke");
      }
      break;
    case 3:
      sp.leftKnee.x_value = accelEvent.acceleration.x;
      sp.leftKnee.y_value = accelEvent.acceleration.y;
      sp.leftKnee.z_value = accelEvent.acceleration.z;
      if((sp.leftKnee.x_value + sp.leftKnee.y_value + sp.leftKnee.z_value) == 0) {
        accSetup(sp.leftKnee.sensorID);
        Serial.println("LK sensor broke");
      }
      break;

  }
}
/*-----------------------------------------------------*/
/*<<<<<<<<<<<<<<<READING FUNCTIONS<<<<<<<<<<<<<<<<<<<<<*/
/*-----------------------------------------------------*/


/*-----------------------------------------------------*/
/*>>>>>>>>>>>>>>>>SERIAL FUNCTIONS>>>>>>>>>>>>>>>>>>>>>*/
/*-----------------------------------------------------*/
void send_next() {
  serialise(header_id++);
  send_reading_serial();
  new_data = FALSE;
  ack_received = 0;
}

void send_reading_serial() {
  // Serial.println("Sending serial over...");
  // Serial.println(buffer);
  prevTime = millis();  // Starting Timer

  for(int i=0; i<len+2; i++) {
    Serial3.write(buffer[i]); // Serial3 write
  }

  // Serial.print("LHAND Values: ");
  // Serial.print(sp.leftHand.x_value);
  // Serial.print(" , ");
  // Serial.print(sp.leftHand.y_value);
  // Serial.print(" , ");
  // Serial.println(sp.leftHand.z_value);
  // Serial.print("RHAND Values: ");
  // Serial.print(sp.rightHand.x_value);
  // Serial.print(" , ");
  // Serial.print(sp.rightHand.y_value);
  // Serial.print(" , ");
  // Serial.println(sp.rightHand.z_value);
  // Serial.print("LKNEE Values: ");
  // Serial.print(sp.leftKnee.x_value);
  // Serial.print(" , ");
  // Serial.print(sp.leftKnee.y_value);
  // Serial.print(" , ");
  // Serial.println(sp.leftKnee.z_value);
  // Serial.print("RKNEE Values: ");
  // Serial.print(sp.rightKnee.x_value);
  // Serial.print(" , ");
  // Serial.print(sp.rightKnee.y_value);
  // Serial.print(" , ");
  // Serial.println(sp.rightKnee.z_value);
}

void serialise(int id) {
  // xSemaphoreTake(mutex, (TickType_t) 1);
  char checksum = 0;

  // Append header ID to buffer
  itoa(id, headID, 10);
  strcat(buffer, headID);
  // buffer[0] = id + '0';
  strcat(buffer, ",");

  createMessage();

  len = strlen(buffer);
  for(int i=0; i<len-1; i++) {
    checksum ^= buffer[i];
    // Serial.print("buffer[");
    // Serial.print(i);
    // Serial.print("] = \'");
    // Serial.print(buffer[i]);
    // Serial.print("\', checksum = \'");
    // Serial.print(checksum);
    // Serial.println("\'");
  }
  // Append checksum to buffer
  itoa(checksum, checksumChar, 10);
  strcat(buffer, checksumChar);
  strcat(buffer, ",");
  // buffer[len] = checksum;
  // Serial.print("Checksum = \'");
  // Serial.print(checksum);
  // Serial.print("\' checksumChar = ");
  // Serial.println(checksumChar);

  len = strlen(buffer);
  // Serial.print("Last in buffer is ");
  // Serial.print(buffer[len]);
  // Serial.println();
  buffer[len+1] = '\n'; // append \n to back of string
  // xSemaphoreGive(mutex);
}

void createMessage() {
  // Serial.println("Creating string~~~");
  // Converting int to characters

  // rightHand
  itoa(sp.rightHand.sensorID, rightHand_id, 10);
  strcat(buffer, rightHand_id);
  strcat(buffer, ",");
  ftoa(rightHand_x, sp.rightHand.x_value, 2);
  strcat(buffer, rightHand_x);
  strcat(buffer, ",");
  ftoa(rightHand_y, sp.rightHand.y_value, 2);
  strcat(buffer, rightHand_y);
  strcat(buffer, ",");
  ftoa(rightHand_z, sp.rightHand.z_value, 2);
  strcat(buffer, rightHand_z);
  strcat(buffer, ",");

  // leftHand
  itoa(sp.leftHand.sensorID, leftHand_id, 10);
  strcat(buffer, leftHand_id);
  strcat(buffer, ",");
  ftoa(leftHand_x, sp.leftHand.x_value, 2);
  strcat(buffer, leftHand_x);
  strcat(buffer, ",");
  ftoa(leftHand_y, sp.leftHand.y_value, 2);
  strcat(buffer, leftHand_y);
  strcat(buffer, ",");
  ftoa(leftHand_z, sp.leftHand.z_value, 2);
  strcat(buffer, leftHand_z);
  strcat(buffer, ",");

  // // rightKnee
  // itoa(sp.rightKnee.sensorID, rightKnee_id, 10);
  // strcat(buffer, rightKnee_id);
  // strcat(buffer, ",");
  // ftoa(rightKnee_x, sp.rightKnee.x_value, 2);
  // strcat(buffer, rightKnee_x);
  // strcat(buffer, ",");
  // ftoa(rightKnee_y, sp.rightKnee.y_value, 2);
  // strcat(buffer, rightKnee_y);
  // strcat(buffer, ",");
  // ftoa(rightKnee_z, sp.rightKnee.z_value, 2);
  // strcat(buffer, rightKnee_z);
  // strcat(buffer, ",");
  //
  // // leftKnee
  // itoa(sp.leftKnee.sensorID, leftKnee_id, 10);
  // strcat(buffer, leftKnee_id);
  // strcat(buffer, ",");
  // ftoa(leftKnee_x, sp.leftKnee.x_value, 2);
  // strcat(buffer, leftKnee_x);
  // strcat(buffer, ",");
  // ftoa(leftKnee_y, sp.leftKnee.y_value, 2);
  // strcat(buffer, leftKnee_y);
  // strcat(buffer, ",");
  // ftoa(leftKnee_z, sp.leftKnee.z_value, 2);
  // strcat(buffer, leftKnee_z);
  // strcat(buffer, ",");

  // torso
  itoa(sp.torso.sensorID, torso_id, 10);
  strcat(buffer, torso_id);
  strcat(buffer, ",");
  ftoa(torso_x, sp.torso.x_value, 2);
  strcat(buffer, torso_x);
  strcat(buffer, ",");
  ftoa(torso_y, sp.torso.y_value, 2);
  strcat(buffer, torso_y);
  strcat(buffer, ",");
  ftoa(torso_z, sp.torso.z_value, 2);
  strcat(buffer, torso_z);
  strcat(buffer, ",");
  ftoa(torso_g_x, sp.torso.g_x_value, 2);
  strcat(buffer, torso_g_x);
  strcat(buffer, ",");
  ftoa(torso_g_y, sp.torso.g_y_value, 2);
  strcat(buffer, torso_g_y);
  strcat(buffer, ",");
  ftoa(torso_g_z, sp.torso.g_z_value, 2);
  strcat(buffer, torso_g_z);
  strcat(buffer, ",");

  // Power reading
  ftoa(volt, voltage, 2);
  strcat(buffer, volt);
  strcat(buffer, ",");
  ftoa(curr, current, 2);
  strcat(buffer, curr);
  strcat(buffer, ",");

  // Serial.print("Voltage = ");
  // Serial.print(voltage);
  // Serial.print(" Current = ");
  // Serial.println(current);
}

void send_reading(void *p) {
  const TickType_t srFrequency = SRFREQ;
  while (1) {
// /*
//   Debugging
// */
// Serial.print("Current time serial mutex = ");
// Serial.println(millis());

    if (xSemaphoreTake(mutex, (TickType_t) 1000)) {
      // Serial.println("------SEND READING FUNC------");

      if (Serial3.available()) {
        response = Serial3.read();
      }
      Serial.print("Response = ");
      Serial.println(response);

      if (header_id == 0) {
        prevTime = millis();
      }
// prevTime = millis();

      if (response == 'A') {
        currTime = millis() - prevTime;
        Serial.print("Ack, RTT = ");
        Serial.println(currTime);
        reset_variables(response);
      } else if (response == 'N') {
        Serial.println("Duplicate data send, skipping...");
        reset_variables(response);
      } else if (response == 'R') {
        Serial.println("Request previous buffer...");
        send_reading_serial();
        reset_variables(response);
      } else if (response == 'H'){
        Serial.println("Request for handshake...");
        vTaskSuspendAll();
        initialise_handshake();
        xTaskResumeAll();
        reset_variables(response);
      } else if (millis() - prevTime > TIMEOUT_SERIAL) {
        if (first_try) {
          Serial.println("Trying to get ACK...");
          // Reset prevTime
          send_reading_serial();
          first_try = FALSE;
        } else {
          Serial.println("Lost connections...");
          response = 'T';
          vTaskSuspendAll();
          initialise_handshake();
          send_reading_serial();
          xTaskResumeAll();
        }
        reset_variables(response);
      } else {
        response = 0;
        // Serial.print("NewDataFlag = ");
        // Serial.print(new_data);
        // Serial.print("; ack_received =  ");
        // Serial.println(ack_received);
      }

      // New data available and Ack for previous packet received
      // Sending next packet
      if (new_data && ack_received) {
        send_next();
      }

      xSemaphoreGive(mutex);
    }

// Serial.print("Current time end serial = ");
// Serial.println(millis());

    vTaskDelay(srFrequency);
  }
}
/*-----------------------------------------------------*/
/*<<<<<<<<<<<<<<<<SERIAL FUNCTIONS<<<<<<<<<<<<<<<<<<<<<*/
/*-----------------------------------------------------*/

void reset_variables(char res) {
  switch (res) {
    case 'A': case 'N':
      strcpy(buffer, "");
      // memset(buffer, 0, sizeof buffer);
      ack_received = 1;
      response = 0;
      first_try = TRUE;
      break;
    case 'R':
      first_try = TRUE;
      response = 0;
      break;
    case 'H':
      response = 0;
      first_try = TRUE;
      prevTime = millis();
      break;
    case 'T':
      header_id =0;
      ack_received = 1; // resetting purpose
      response = 0;
      new_data = FALSE;
      first_try = TRUE;
      prevTime = millis();
      strcpy(buffer, "");
      // memset(buffer, 0, sizeof buffer);
      break;
    default: break;
  }
}

void accSetup(int num) {
  int port = 0;
  switch (num) {
    case 0:
      port = RHAND_PIN;
      digitalWrite(LHAND_PIN, HIGH);
      // Serial.println("testLH");
      // digitalWrite(LKNEE_PIN, HIGH);
      // Serial.println("testLK");
      // digitalWrite(RKNEE_PIN, HIGH);
      // Serial.println("test0");
      break;
    case 1:
      port = LHAND_PIN;
      digitalWrite(RHAND_PIN, HIGH);
      // Serial.println("testRH");
      // digitalWrite(LKNEE_PIN, HIGH);
      // Serial.println("testLK");
      // digitalWrite(RKNEE_PIN, HIGH);
      // Serial.println("test1");
      break;
    case 2:
      port = RKNEE_PIN;
      digitalWrite(LHAND_PIN, HIGH);
      digitalWrite(RHAND_PIN, HIGH);
      digitalWrite(LKNEE_PIN, HIGH);
      // Serial.println("test2");
      break;
    case 3:
      port = LKNEE_PIN;
      digitalWrite(LHAND_PIN, HIGH);
      digitalWrite(RHAND_PIN, HIGH);
      // digitalWrite(RKNEE_PIN, HIGH);
      // Serial.println("test3");
      break;
  }
  // Serial.println("test outside switch");
  digitalWrite(port, LOW);
  Serial.print("Port activated = ");
  Serial.println(port);

  if(!accel.begin()) {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("Ooops, no ADXL345 detected ... Check your wiring!");
    while(1);
  }
// Serial.println("test after accel begin");
  // /* Set the range to whatever is appropriate for your project */
  accel.setRange(ADXL345_RANGE_2_G);
  accel.setDataRate(ADXL345_DATARATE_200_HZ);

  digitalWrite(port, HIGH);
}

void initialise_handshake(void) {
  Serial.println("Initialising handshake protocol...");

  while (!handshake_done) {
    if (Serial3.available()) {
      char readByte = Serial3.read();
      if (readByte == 'H') {
        Serial3.flush();
        Serial3.write('A');
        Serial.print(readByte);
        Serial.print(" ");
        Serial.println(ack_flag);
        // Start timer for RTT calculation
        RTT_prevTime = millis();
        // Serial.print("RTT prevTime = ");
        // Serial.println(RTT_prevTime);
        ack_flag = 1;
        Serial.println("Received Hello from Pi.");
      } else if ((readByte == 'A')&&(ack_flag == 1)) {
        RTT_currTime = millis() - RTT_prevTime;
        handshake_done = TRUE;
        Serial.println("Handshaking done! Sweaty palms~");
        if (handshake_first) {
          handshake_first = FALSE;
          RTT_TIMEOUT = RTT_currTime;
          // Serial.print("RTT_currTime = ");
          // Serial.println(RTT_currTime);
          TIMEOUT_SERIAL = TIMEOUT_VAR * TIMEOUT_EST +
                          (1 - TIMEOUT_VAR) * RTT_TIMEOUT;
          Serial.print("TIMEOUT for data is ");
          Serial.println(TIMEOUT_SERIAL);
          prevTime = millis();
        }
      } else if (ack_flag && ((millis() - prevTime)>TIMEOUT_HANDSHAKE)) {
        Serial.println("Timeout waiting for A");
        ack_flag = 0;
      } else {
        Serial.print(readByte);
        Serial.println(" : wrong byte..");
      }
    }
  }
  handshake_done = FALSE;
  ack_flag = 0;
}


void setup() {
  sp.rightHand.sensorID = 0;
  sp.leftHand.sensorID = 1;
  sp.rightKnee.sensorID = 2;
  sp.leftKnee.sensorID = 3;
  sp.torso.sensorID = 4;

  pinMode(LHAND_PIN, OUTPUT);
  pinMode(RHAND_PIN, OUTPUT);
  // pinMode(LKNEE_PIN, OUTPUT);
  // pinMode(RKNEE_PIN, OUTPUT);

  // // Pins are perpetually set to HIGH
  // digitalWrite(LHAND_PIN, HIGH);
  // digitalWrite(RHAND_PIN, HIGH);
  // digitalWrite(LKNEE_PIN, HIGH);
  // digitalWrite(RKNEE_PIN, HIGH);

  pinMode(CURRENT_PIN, INPUT);
  pinMode(VOLTAGE_PIN, INPUT);

  Serial.begin(115200);
  Serial3.begin(115200);

  Serial.println("Arduino Powering up....");
Serial.println("test1");
  Wire.begin();
Serial.println("testwire");
  mpu6050.begin();
Serial.println("test2");
  // mpu6050.calcGyroOffsets(true);
  mpu6050.setGyroOffsets(-2.30, -0.73, 1.40);
Serial.println("test3");
  // Setting up the accelerometer
  for (int i=0 ; i<2; i++) {
    // if(i != 2)
      accSetup(i);
  }

  initialise_handshake();
  // TIMEOUT_SERIAL = TIMEOUT_EST/2;

  xTaskCreate(read_sensor, "Reading Sensor", STACK_SIZE, NULL, 1, NULL);
  xTaskCreate(send_reading, "Sending Reading", STACK_SIZE, NULL, 2, NULL);
  vTaskStartScheduler();
}

void loop() {

}

/*
  The following ftoa code is written by MartinWaller (2011)
  Taken from https://forum.arduino.cc/index.php?topic=63721.0
*/
char *ftoa(char *fbuffer, double d, int precision) {
	long wholePart = (long) d;

	// Deposit the whole part of the number.
	itoa(wholePart,fbuffer,10);

	// Now work on the faction if we need one.
	if (precision > 0) {
		// We do, so locate the end of the string and insert
		// a decimal point.
		char *endOfString = fbuffer;
		while (*endOfString != '\0') endOfString++;
		*endOfString++ = '.';

		// Now work on the fraction, be sure to turn any negative
		// values positive.
		if (d < 0) {
			d *= -1;
			wholePart *= -1;
		}

		double fraction = d - wholePart;
		while (precision > 0) {

			// Multipleby ten and pull out the digit.
			fraction *= 10;
			wholePart = (long) fraction;
			*endOfString++ = '0' + wholePart;

			// Update the fraction and move on to the
			// next digit.
			fraction -= wholePart;
			precision--;
		}

		// Terminate the string.
		*endOfString = '\0';
	}
   return fbuffer;
}
