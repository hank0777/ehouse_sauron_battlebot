/*
    Controls team PSU Ehouse Combat Robotics
    Hi! Hello! Git is Amazing - Peter
    test test test, hi!! - Tiffany
*/

void setup() {
   
}

void loop() {

}

double NormalizeValue(double value) {

    if(value < 1000) {
        value = 1000;
    }
    if(value > 2000) {
        value = 2000;
    }
    return value;
}