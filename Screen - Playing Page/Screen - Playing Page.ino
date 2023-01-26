#include <Arduino.h>
#include <U8g2lib.h>
#include <PinButton.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

#define fontName u8g2_font_6x10_tf

#define SOFT_DEBOUNCE_MS 100
PinButton btnSel(5);
#define pinA 2
#define pinB 3

int rewrite = 0;
int currentState;
int lastState;
int counter = 0;
int i = 0;
int start;

int optionSelection;
int difficulty;
int currentPage;

bool selected = false;
bool dial = false;
bool print = false;
bool reading = false;

String pieces_player = "P";
String kings_player = "K";
String pieces_computer = "P";
String kings_computer = "K";
String msg = "";

String text = "";
u8g2_uint_t textLength;

// Screen info
U8G2_SH1106_128X64_NONAME_1_HW_I2C display(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
u8g2_uint_t width = 128;
u8g2_uint_t height = 64;
u8g2_uint_t margin = 4;

u8g2_uint_t originX = 0 + margin - 2;
u8g2_uint_t originY = 0 + margin*2;
u8g2_uint_t lineHeight = margin;

// Handle encoder (turning)
void doEncoder() {
  currentState = digitalRead(pinA);

  if (currentPage == 1 || currentPage == 2){
    if(currentState != lastState && currentState == 1){
      if (dial == true){
        if (currentState == digitalRead(pinB)) {
          if (difficulty >= 2){
            difficulty--;
          }
        } else {
          if (difficulty <= 4){
            difficulty++;
          }
        }
      } else {
        if (currentState == digitalRead(pinB)) {
          if (optionSelection == 1){
            optionSelection--;
          }
        } else {
          if (optionSelection == 0){
            optionSelection++;
          }
        }
      }
    }
  }

  lastState = currentState;
}

void setup() {
  Serial.begin(9600);
  start = millis();
  difficulty = 1;
  currentPage = 0;
  optionSelection = 0;

  display.begin();
  display.setFont(fontName);

  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, INPUT_PULLUP);
  attachInterrupt(0, doEncoder, CHANGE);

  lastState = digitalRead(pinA);
}

void reset(){
  currentPage = 0;
  selected = false;
  dial = false;
  print = false;
  reading = false;
  msg = "";

  rewrite = 0;
  counter = 0;
  i = 0;

  pieces_player = "12";
  kings_player = "0";
  pieces_computer = "12";
  kings_computer = "0";
}

void loop() {
  // Handle the press of the rotary encoder button
  btnSel.update();
  if (btnSel.isSingleClick()){
    if(currentPage == 0){
      dial = true;
      currentPage++;
    }
    
    else if(currentPage == 1 && dial == true){
      dial = false;
      optionSelection = 1;
    }

    else if(currentPage == 1 && dial == false && optionSelection == 1){
      currentPage++;
      optionSelection = 1;
    }

    else if(currentPage == 1 && dial == false && optionSelection == 0){
      currentPage--;
    }

    else if(currentPage == 2 && optionSelection == 1){
      if (Serial.available() == 0){
        String string = "";
        switch(difficulty){
          case 1:
            string = "1";
            break;
          case 2:
            string = "2";
            break;
          case 3:
            string = "3";
            break;
          case 4:
            string = "4";
            break;
          case 5:
            string = "5";
            break;
        }
        Serial.println("dif: " + string);
        Serial.flush();

        reading = true;
      }
    }

    else if(currentPage == 2 && optionSelection == 0){
      dial = true;
      optionSelection = 0;
      currentPage--;
    }
  }

  // Handles the display, with a refresh timing of 100 milliseconds
  // to secure a smoother display
  if (millis()-rewrite > 100){
    display.firstPage();
    do{
      if (currentPage == 0){
        startPage();
      } else if (currentPage == 1){
        difficultyPage();
      } else if (currentPage == 2){
        initializeGamePage();
      } else if (currentPage == 3){
        gamePage();
      }
    } while(display.nextPage());

    rewrite = millis();
  }

  if (Serial.available() > 0 && reading == true){
    msg = Serial.readStringUntil('\n');

    if (msg == "reset"){
      reset();
    }
    
    if (msg == "stop"){
      currentPage++;
    } else {
      pieces_player = getValue(msg, ';', 0);
      kings_player = getValue(msg, ';', 1);
      pieces_computer = getValue(msg, ';', 2);
      kings_computer = getValue(msg, ';', 3);
    }
  }

  delay(10);
}

// First page shown on startup of the Arduino
void startPage(){
  display.setFont(fontName);
  display.drawStr(originX, originY, "Welcome, to start a");
  display.drawStr(originX, originY + 3*lineHeight, "game press the button");
  display.drawStr(originX, originY + 6*lineHeight, "in the center.");

  // Requires a text (string) and an location (int), correction (int) and blinkDelay (int)
  // NOTE: location (int) refers to the type of displaying
  selectOption("Start", 0, 0, 48);
}

// Page where the player can select the difficulty of the AI
// NOTE: Limited to a max of 5
void difficultyPage(){
  display.setFont(fontName);
  String string = "Game difficulty: ";
  display.drawStr((width - display.getStrWidth(string.c_str()))/2, originY + margin, string.c_str());

  difficultyDial();

  // If the difficulty has been selected
  // EXTRA:
  // Requires a text (string) and an location (int), correction (int) and blinkDelay (int)
  // NOTE: location (int) refers to the type of displaying
  selectOption("Back", 1, 0, 96);
  selectOption("Continue", 2, 10, 96);
}

void initializeGamePage(){
  display.setFont(fontName);
  display.drawStr(originX, originY, "Prepare the board");
  display.drawStr(originX, originY + 3*lineHeight, "and select start to");
  display.drawStr(originX, originY + 6*lineHeight, "begin playing.");

  selectOption("Back", 1, 0, 96);
  selectOption("Start", 2, 10, 96);
}

void gamePage(){
  display.setFont(fontName);
  String dif = "";
        switch(difficulty){
          case 1:
            dif = "1";
            break;
          case 2:
            dif = "2";
            break;
          case 3:
            dif = "3";
            break;
          case 4:
            dif = "4";
            break;
          case 5:
            dif = "5";
            break;
        }
  String string = "PLAYING -  DIF: " + dif;
  display.drawStr((width - display.getStrWidth("====================="))/2, originY, "=====================");
  display.drawStr((width - display.getStrWidth(string.c_str()))/2, originY + margin*2, string.c_str());
  display.drawStr((width - display.getStrWidth("====================="))/2, originY + 4*margin, "=====================");

  string = "Player:";
  u8g2_uint_t fourSections = (width)/4;
  display.drawStr(fourSections-(display.getStrWidth(string.c_str())/2), originY + 7*margin, string.c_str());
  display.drawStr(2*fourSections, originY + 7*margin, pieces_player.c_str());
  display.drawStr(3*fourSections, originY + 7*margin, kings_player.c_str());

  
  string = "Computer:";
  display.drawStr(fourSections-(display.getStrWidth(string.c_str())/2), originY + 12*margin, string.c_str());
  display.drawStr(2*fourSections + 5, originY + 12*margin, pieces_computer.c_str());
  display.drawStr(3*fourSections + 10, originY + 12*margin, kings_computer.c_str());
}

// Creates a "dial" which indicates the selected difficulty for the AI
void difficultyDial(){
  u8g2_uint_t maxNumberWidth = 10;
  u8g2_uint_t gapSize = ((width-4)-5*10)/6;
  u8g2_uint_t center = height/2;

  // First place
  display.setCursor(gapSize, center);
  if(difficulty >= 3){
    display.print(difficulty-2);
  } else{
    display.print(" ");
  }

  // Second place
  display.setCursor(gapSize*2 + maxNumberWidth, center);
  if(difficulty >= 2){
    display.print(difficulty-1);
  } else{
    display.print(" ");
  }

  // Center
  display.setFont(u8g2_font_7x14B_tf);
  display.setCursor(gapSize*3 + 2*maxNumberWidth, center);
  display.print(difficulty);
  display.setFont(fontName);

  // Third place
  display.setCursor(gapSize*4 + 3*maxNumberWidth, center);
  if (difficulty <= 4){
    display.print(difficulty+1);
  } else {
    display.print(" ");
  }

  // Fourth place
  display.setCursor(gapSize*5 + 4*maxNumberWidth, center);
  if (difficulty <= 3){
    display.print(difficulty+2);
  } else {
    display.print(" ");
  }
}

// Shows which option is selected by blinking the text
void selectOption(String option, int location, int correction, int delayTime){
  if (i == delayTime){
    selected = !selected;
    i = 0;
  }

  if (currentPage == 0){
    blinkText(option);
    display.setFont(u8g2_font_7x14_tf);
  } else if (currentPage == 1 && dial == false && option == "Back" && optionSelection == 0){
    blinkText(option);
  } else if(currentPage == 1 && dial == false && option == "Continue" && optionSelection == 1){
    blinkText(option);
  } else if (currentPage == 2 && option == "Back" && optionSelection == 0){
    blinkText(option);
  } else if(currentPage == 2 && option == "Start" && optionSelection == 1){
    blinkText(option);
  } else {
    text = option;
    textLength = display.getStrWidth(text.c_str());
  }

  if(location == 0){
    display.drawStr((width-textLength)/2, height-10, text.c_str());
  } else if (location == 1){
    display.drawStr((width/4)-(textLength/2), height-10, text.c_str());
  } else if (location == 2){
    display.drawStr((3*(width/4))-(textLength/2)-correction, height-10, text.c_str());
  }

  i++;
}

void blinkText(String option){
  if (selected == false){
    text = option;
    textLength = display.getStrWidth(text.c_str());
  } else if (selected == true) {
    text = "     ";
    textLength = display.getStrWidth(text.c_str());
  }
}

String getValue(String data, char separator, int index){
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}