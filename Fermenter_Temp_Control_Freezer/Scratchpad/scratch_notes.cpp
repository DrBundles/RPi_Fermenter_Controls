#include <stdio.h>
using namespace std;
/* 
   run in a dev cmd prompt (Visual Studio Tools)
   compile with cl scratch_notes.c
   view results with scratch_notes.exe
*/

// Setpoint Temperature values in degrees Celcius
float tempSP_1 = 19;
float tempSP_2 = 19;

// Temperature Buffer
int buffer_size = 10;
float buffer_temp1[10];
float buffer_temp2[10];
float temp1 = tempSP_1;
float temp2 = tempSP_2;

// Function Definitions
float average(float *temp_p, int array_size);
void shiftArray(float *temp_p, int array_size, float new_val);

int main()
{

  // Initialize the Temperature Buffer
  int ind = 0;
  while(ind <= buffer_size-1){
    buffer_temp1[ind] = tempSP_1;
    buffer_temp2[ind] = tempSP_2;
    ind++;
  }
  printf("test buffer_temp[0] = %4.2f\n", buffer_temp1[0]);
  
  float avg_temp1 = average(buffer_temp1, buffer_size);
  printf("average 1 = %4.2f\n", avg_temp1);
  
   // Update the buffer
  float tempVal_1 = 0.1;
  shiftArray(buffer_temp1, buffer_size, tempVal_1);
  //buffer_temp1[0] = tempVal_1;
  
  avg_temp1 = average(buffer_temp1, buffer_size);
  printf("average 2 = %4.2f\n", avg_temp1);
  
  // Update the buffer
  tempVal_1 = 0.2;
  shiftArray(buffer_temp1, buffer_size, tempVal_1);
  //buffer_temp1[0] = tempVal_1;
  
  avg_temp1 = average(buffer_temp1, buffer_size);
  printf("average 2 = %4.2f\n", avg_temp1);
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
