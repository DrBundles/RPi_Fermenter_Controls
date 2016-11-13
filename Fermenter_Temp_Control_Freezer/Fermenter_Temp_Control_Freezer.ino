/*
  Fermenter temperature control system. 2x control loops for
  independent control of two fermenters. Uses TMP36 Analog 
  temperature sensors and independent relays to control
  heaters.
  
  By Steve Lammers
  
  LOG
  -------------------------
 	 
*/

#include <stdio.h>

// Analog temperature pins
const int tempPin_1 = A3;//A2;
const int tempPin_2 = A2;//A3;

// Digital relay pins
const int relayPin_1 = 13;//7;
const int relayPin_2 = 10;//8;

// Heating / Cooling FLAG
int heat_cool_FLAG = 0; // 0: Cooling, 1: Heating

// Current Temperature values in degrees Celcius
float tempVal_1 = 0;
float tempVal_2 = 0;

// Setpoint Temperature values in degrees Celcius
float tempSP_1 = 18; //2; //24; //20; //21; //2; //4; //19.4; //17.7; //4, 19
float tempSP_2 = 18; //2; //24; //20; //21; //2; //4; //19.4; //17.7; //4, 19

// Thermometer calibration values
float calib_temp1 = 2.36; // Add this val to measured
float calib_temp2 = 1.34; // Add this val to measured

// Temperature Buffer
int buffer_size = 10;
float buffer_temp1[10];
float buffer_temp2[10];
float temp1 = tempSP_1;
float temp2 = tempSP_2;

// Function Definitions
float average(float *temp_p, int array_size);
void shiftArray(float *temp_p, int array_size, float new_val);

void setup()
{
  // Initialize the serial communication
  Serial.begin(9600);
  // Initialize Pins 
  pinMode(relayPin_1, OUTPUT);
  pinMode(relayPin_2, OUTPUT);
  // Initialize the Temperature Buffer
  int ind = 0;
  while(ind <= buffer_size-1){
    buffer_temp1[ind] = tempSP_1;
    buffer_temp2[ind] = tempSP_2;
    ind++;
  }
  digitalWrite(relayPin_1, LOW); // Turn cooling off
  digitalWrite(relayPin_2, LOW); // Turn heating off
}

void loop()
{
  // Temp (deg C) = 100*V-50
  tempVal_1 = 100*(5.0*analogRead(tempPin_1)/1024)-50 + calib_temp1;
  tempVal_2 = 100*(5.0*analogRead(tempPin_2)/1024)-50 + calib_temp2;
  
  // Update the buffer
  shiftArray(buffer_temp1, buffer_size, tempVal_1);
  temp1 = average(buffer_temp1, buffer_size);
  shiftArray(buffer_temp2, buffer_size, tempVal_2);
  temp2 = average(buffer_temp2, buffer_size);
  
  
  // Output values to serial
  Serial.print("Temp_1 = ");
  Serial.println(temp1);
  Serial.print("Temp_2 = ");
  Serial.println(temp2);
  
  if (temp1 > tempSP_1 + 0.5) 
  {
    Serial.println("Cooling");
    heat_cool_FLAG = 0; // 0: Cooling, 1: Heating
    digitalWrite(relayPin_1, LOW); // Turn cooling on
    digitalWrite(relayPin_2, HIGH);  // Turn heating off
  }
  if (temp1 < tempSP_1 - 0.5) 
  {
    Serial.println("Heating");
    heat_cool_FLAG = 1; // 0: Cooling, 1: Heating
    digitalWrite(relayPin_1, HIGH);  // Turn cooling off
    digitalWrite(relayPin_2, LOW); // Turn heating on
  }
  
  // If the system is heating or cooling and reaches setpoint, then stop heating or cooling
  if (temp1 < tempSP_1 - 0.25 && heat_cool_FLAG == 0)
    {
      Serial.println("Holding");
      digitalWrite(relayPin_1, HIGH);  // Turn cooling off
      digitalWrite(relayPin_2, HIGH);  // Turn heating off
    }
 
   if (temp1 > tempSP_1 + 0.25 && heat_cool_FLAG == 1)
    {
      Serial.println("Holding");
      digitalWrite(relayPin_1, HIGH);  // Turn cooling off
      digitalWrite(relayPin_2, HIGH);  // Turn heating off
    }
 
  delay(1000);
  
}



float average(float *temp_p, int array_size)
{
   int ind = 0;
   float sumVal = 0;
   float average = 0;

   while(ind < array_size){
     sumVal += temp_p[ind];
	 printf("sumVal %d: %4.2f\n", ind, sumVal);
     ind++;
   }

   average = sumVal / array_size;
   
   return average;
}


void shiftArray(float *temp_p, int array_size, float new_val)
{
   int ind = 0;
   float sumVal = 0;
   float average = 0;

   while(ind < array_size-1){
     temp_p[ind] = temp_p[ind+1];
     ind++;
   }
   
   temp_p[array_size-1] = new_val;
}
