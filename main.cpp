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
    /*
    Forces a double into a range 1000.0 - 2000.0
    */
    if(value < 1000) {
        value = 1000;
    }
    if(value > 2000) {
        value = 2000;
    }
    return value;
}