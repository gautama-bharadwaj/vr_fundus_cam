#include <Adafruit_NeoPixel.h>

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN 6

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 24 // Popular NeoPixel ring size

// When setting up the NeoPixel library, we tell it how many pixels,
// and which pin to use to send signals. Note that for older NeoPixel
// strips you might need to change the third parameter -- see the
// strandtest example for more information on possible values.
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// Defining delays
#define off_time 5000 
#define on_time 200

int x;

void setup() {
  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop() {  
  
   while (!Serial.available());
   x = Serial.readString().toInt();
   Serial.print(x);
   if (x==-1){
    pixels.clear();
   }
   else if (x==0){
      for(int i=0; i<NUMPIXELS; i++) { 
        // For each pixel...
        pixels.setPixelColor(i, pixels.Color(200, 0, 0));
      }   
      // Send the updated pixel colors to the hardware.
      pixels.show();
      delay(on_time);
   }
   else if (x==1){
      for(int i=0; i<NUMPIXELS; i++) { 
        // For each pixel...
        pixels.setPixelColor(i, pixels.Color(0, 200, 0));
      }
      // Send the updated pixel colors to the hardware.
      pixels.show();
      delay(on_time);
   }
   else if (x==2){
      for(int i=0; i<NUMPIXELS; i++) { 
        // For each pixel...
        pixels.setPixelColor(i, pixels.Color(0, 0, 200));
      }
      // Send the updated pixel colors to the hardware.
      pixels.show();
      delay(on_time);
   }
   else if (x==3){
      for(int i=0; i<NUMPIXELS; i++) { 
        // For each pixel...
        pixels.setPixelColor(i, pixels.Color(200, 0, 200));
      }
      // Send the updated pixel colors to the hardware.
      pixels.show();
      delay(on_time);
   }
   else {
      for(int i=0; i<NUMPIXELS; i++) { 
        // For each pixel...
        pixels.setPixelColor(i, pixels.Color(200, 200, 0));
      }
      // Send the updated pixel colors to the hardware.
      pixels.show();
      delay(on_time);
   }
   
    pixels.clear(); 
    pixels.show();
}
