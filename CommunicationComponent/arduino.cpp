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
int LHAND_PIN = 52; int RHAND_PIN = 42;
int LKNEE_PIN = 38; int RKNEE_PIN = 48;

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
  1. Please change the encoding in rpi, to ("A").encode(), etc
  2. Please add/change these lines to the bottom of the while(True)
          voltage = float(packet.rsplit(',',2)[1])
          print("Voltage: ", voltage)
          current = float(packet.rsplit(',',2)[2])
          print("Current: ", current)
          ser.write(ack)
  3. TODO: make an array out of the string in rPi
**********************************************************************/


/*-----------------------------------------------------*/
/*>>>>>>>>>>>>>>>READING FUNCTIONS>>>>>>>>>>>>>>>>>>>>>*/
/*-----------------------------------------------------*/
void read_sensor(void *p) {
  TickType_t rsLastWakeTime;
  const TickType_t rsFrequency = 120;
  rsLastWakeTime = xTaskGetTickCount();

  while(1) {
    xSemaphoreTake(mutex, (TickType_t) 10);
    Serial.println("------READ SENSORS FUNC------");

    digitalWrite(LHAND_PIN, HIGH);
    read_ACC(sp.leftHand.sensorID);
    digitalWrite(LHAND_PIN, LOW);

    digitalWrite(RHAND_PIN, HIGH);
    read_ACC(sp.rightHand.sensorID);
    digitalWrite(RHAND_PIN, LOW);

    digitalWrite(LKNEE_PIN, HIGH);
    read_ACC(sp.leftKnee.sensorID);
    digitalWrite(LKNEE_PIN, LOW);

    digitalWrite(RKNEE_PIN, HIGH);
    read_ACC(sp.rightKnee.sensorID);
    digitalWrite(RKNEE_PIN, LOW);

    read_IMU();
    read_power();

    new_data = TRUE;
    xSemaphoreGive(mutex);
    /*
        overflow and establish contact again
    */

    // Delay for 5ms, sampling rate = 200Hz
    vTaskDelayUntil(&rsLastWakeTime, rsFrequency);
  }
}

void read_power() {
  Serial.println("Reading Power ...");
  voltage = analogRead(VOLTAGE_PIN);
  current = analogRead(CURRENT_PIN);
}

void read_IMU() {
  Serial.println("Reading  IMU  ...");
  mpu6050.update();
  sp.torso.x_value = mpu6050.getAccX();
  sp.torso.y_value = mpu6050.getAccY();
  sp.torso.z_value = mpu6050.getAccZ();
  sp.torso.g_x_value = mpu6050.getGyroAngleX();
  sp.torso.g_y_value = mpu6050.getGyroAngleY();
  sp.torso.g_z_value = mpu6050.getGyroAngleZ();
}

void read_ACC(int accelNo) {
  Serial.print("Reading Accel");
  Serial.print(accelNo);
  Serial.println("...");

  /*Get a new sensor event */
  sensors_event_t accelEvent;
  accel.getEvent(&accelEvent);

  switch (accelNo) {
    case 0:
      sp.leftHand.x_value = accelEvent.acceleration.x;
      sp.leftHand.y_value = accelEvent.acceleration.y;
      sp.leftHand.z_value = accelEvent.acceleration.z;
      break;
    case 1:
      sp.rightHand.x_value = accelEvent.acceleration.x;
      sp.rightHand.y_value = accelEvent.acceleration.y;
      sp.rightHand.z_value = accelEvent.acceleration.z;
      break;
    case 2:
      sp.leftKnee.x_value = accelEvent.acceleration.x;
      sp.leftKnee.y_value = accelEvent.acceleration.y;
      sp.leftKnee.z_value = accelEvent.acceleration.z;
      break;
    case 3:
      sp.rightKnee.x_value = accelEvent.acceleration.x;
      sp.rightKnee.y_value = accelEvent.acceleration.y;
      sp.rightKnee.z_value = accelEvent.acceleration.z;
      break;

  }
}
/*-----------------------------------------------------*/
/*<<<<<<<<<<<<<<<READING FUNCTIONS<<<<<<<<<<<<<<<<<<<<<*/
/*-----------------------------------------------------*/


/*-----------------------------------------------------*/
/*>>>>>>>>>>>>>>>>SERIAL FUNCTIONS>>>>>>>>>>>>>>>>>>>>>*/
/*-----------------------------------------------------*/
void send_reading_serial() {
  Serial.println("Sending serial over...");
  Serial.println(buffer);
  for(int i=0; i<len+2; i++) {
    Serial3.write(buffer[i]); // Serial3 write
  }
  response = Serial3.read();
  Serial.println(response);
}

void serialise(int id) {
  xSemaphoreTake(mutex, (TickType_t) 10);
  char checksum = 0;

  // Append header ID to buffer
  itoa(id, headID, 10);
  strcat(buffer, headID);
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
  Serial.print("Checksum = \'");
  Serial.print(checksum);
  Serial.print("\' checksumChar = ");
  Serial.println(checksumChar);

  len = strlen(buffer);
  Serial.print("Last in buffer is ");
  Serial.print(buffer[len]);
  Serial.println();
  buffer[len+1] = '\n'; // append \n to back of string
  xSemaphoreGive(mutex);
}

void createMessage() {
  Serial.println("Creating string~~~");
  // Converting int to characters

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

  // leftKnee
  itoa(sp.leftKnee.sensorID, leftKnee_id, 10);
  strcat(buffer, leftKnee_id);
  strcat(buffer, ",");
  ftoa(leftKnee_x, sp.leftKnee.x_value, 2);
  strcat(buffer, leftKnee_x);
  strcat(buffer, ",");
  ftoa(leftKnee_y, sp.leftKnee.y_value, 2);
  strcat(buffer, leftKnee_y);
  strcat(buffer, ",");
  ftoa(leftKnee_z, sp.leftKnee.z_value, 2);
  strcat(buffer, leftKnee_z);
  strcat(buffer, ",");

  // rightKnee
  itoa(sp.rightKnee.sensorID, rightKnee_id, 10);
  strcat(buffer, rightKnee_id);
  strcat(buffer, ",");
  ftoa(rightKnee_x, sp.rightKnee.x_value, 2);
  strcat(buffer, rightKnee_x);
  strcat(buffer, ",");
  ftoa(rightKnee_y, sp.rightKnee.y_value, 2);
  strcat(buffer, rightKnee_y);
  strcat(buffer, ",");
  ftoa(rightKnee_z, sp.rightKnee.z_value, 2);
  strcat(buffer, rightKnee_z);
  strcat(buffer, ",");

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

  Serial.print("Voltage = ");
  Serial.print(voltage);
  Serial.print(" Current = ");
  Serial.println(current);
}
/*-----------------------------------------------------*/
/*<<<<<<<<<<<<<<<<SERIAL FUNCTIONS<<<<<<<<<<<<<<<<<<<<<*/
/*-----------------------------------------------------*/


void send_reading(void *p) {
  TickType_t srLastWakeTime;
  const TickType_t srFrequency = 50;
  srLastWakeTime = xTaskGetTickCount();
  while (1) {
    Serial.println("------SEND READING FUNC------");

    if (Serial3.available()) {
      response = Serial3.read();
    }
    // Serial.print("Response = ");
    // Serial.println(response);
    if (response == 'A') {
      Serial.println("Acknowledgment received from rPi");
      strcpy(buffer, "");
      ack_received = 1;
      response = 0;
    } else if (response == 'N') {
      Serial.println("Resending previous buffer...");
      send_reading_serial();
      response = 0;
    } else if (response == 'H'){
      header_id = 0;
      handshake_done = 0;
      ack_flag = 0;
      response = 0;
      Serial.println("Request for handshake...");
      initialise_handshake();
    } else {
      response = 0;
      Serial.print("NewDataFlag = ");
      Serial.print(new_data);
      Serial.print("; ack_received =  ");
      Serial.println(ack_received);
    }

    if (new_data && ack_received) {
      serialise(header_id++);
      send_reading_serial();
      new_data = FALSE;
      ack_received = 0;
    }

    vTaskDelayUntil(&srLastWakeTime, srFrequency);
  }
}

void accSetup(int num) {
  int port = 0;
  switch (num) {
    case 0: port = LHAND_PIN; break;
    case 1: port = RHAND_PIN; break;
    case 2: port = LKNEE_PIN; break;
    case 3: port = RKNEE_PIN; break;
  }

  digitalWrite(port, HIGH);
  Serial.print("Port activated = ");
  Serial.println(port);
  //
  // if(!accel.begin()) {
  //   /* There was a problem detecting the ADXL345 ... check your connections */
  //   Serial.println("Ooops, no ADXL345 detected ... Check your wiring!");
  //   while(1);
  // }
  //
  // /* Set the range to whatever is appropriate for your project */
  // accel.setRange(ADXL345_RANGE_2_G);
  // accel.setDataRate(ADXL345_DATARATE_200_HZ);

  digitalWrite(port, LOW);
}

void initialise_handshake(void) {
  while(!handshake_done) {
    if(Serial3.available()) {
      // Serial.println("Inside");
      char readByte = Serial3.read();
      if(readByte == 'H') {
        Serial3.write('A');
        ack_flag = 1;
        Serial.println("Received Hello from Pi.");
      } else if((readByte == 'A')&&(ack_flag == 1)) {
        handshake_done = 1;
        Serial.println("Handshaking done! Sweaty palms~");
      } else {
        Serial.print(readByte);
        Serial.println(" : wrong byte..");
        // Serial3.write('R');
      }
    }
  }
}


void setup() {
  sp.leftHand.sensorID = 0;
  sp.rightHand.sensorID = 1;
  sp.leftKnee.sensorID = 2;
  sp.rightKnee.sensorID = 3;
  sp.torso.sensorID = 4;

  pinMode(LHAND_PIN, OUTPUT);
  pinMode(RHAND_PIN, OUTPUT);
  pinMode(LKNEE_PIN, OUTPUT);
  pinMode(RKNEE_PIN, OUTPUT);

  pinMode(CURRENT_PIN, INPUT);
  pinMode(VOLTAGE_PIN, INPUT);

  Serial.begin(115200);
  Serial3.begin(115200); // To be changed when using Mega

  Serial.println("Arduino Powering up....");

  Wire.begin();
  mpu6050.begin();
  // mpu6050.calcGyroOffsets(true);
  mpu6050.setGyroOffsets(-2.30, -0.73, 1.40);

  // Setting up the accelerometer
  for (int i =0 ; i<4; i++) {
    accSetup(i);
  }

  Serial.println("Initialising handshake protocol...");
  initialise_handshake();

  xTaskCreate(read_sensor, "Reading Sensor", STACK_SIZE, NULL, 1, NULL);
  xTaskCreate(send_reading, "Sending Reading", STACK_SIZE, NULL, 2, NULL);
  // Serial.println("Start scheduler");
  vTaskStartScheduler();
  Serial.println("Debug");
}

void loop() {

}

/*
  The following ftoa code is written by MartinWaller (2011)
  Taken from https://forum.arduino.cc/index.php?topic=63721.0
*/
char *ftoa(char *buffer, double d, int precision) {
	long wholePart = (long) d;

	// Deposit the whole part of the number.
	itoa(wholePart,buffer,10);

	// Now work on the faction if we need one.
	if (precision > 0) {
		// We do, so locate the end of the string and insert
		// a decimal point.
		char *endOfString = buffer;
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
   return buffer;
}
