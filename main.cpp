/*
    Controls team PSU Ehouse Combat Robotics
    Hi! Hello! Git is Amazing - Peter
    test test test, hi!! - Tiffany
    test test test test test
*/
using namespace std;

double NormalizeValue(double value);
double applyRateProfile(double inputValue, double maxRate, double centerSensitivity, double expo);
void MixRCCommands(double xInput, double yInput, double &motorInputs);
double *motorInputs[2]; // motorInputs[0] - left motor, motorInputs[1] - right motor


// setup runs only once
void setup() {
   
}

// loop will run indefinitely
void loop() {

}



// Custom functions below this line -------------------------------------------------

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

double applyRateProfile(double inputValue, double maxRate, double centerSensitivity, double expo) {
    /*
    Applies a rate profile to an input value.
    Args:
        inputValue: input value range 0.0 - 100.0
    Returns:
        output in range 0.0 - 100.0
    */
    double output = inputValue;
    return output;
}

void MixRCCommands(double xInput, double yInput, double &motorInputs) {
    /*
    x/yInput range: 0.0 - 100.0
    Mapping:
        (0, 0) - bottom left corner and (100, 100) - top right corner
        (0, 0) - bottom middle/straight backwards and (100, 100) - top middle/straight forwards
    */
}