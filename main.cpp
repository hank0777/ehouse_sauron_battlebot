/*
    Controls team PSU Ehouse Combat Robotics

*/
#include<cmath>

using namespace std;


double NormalizeValue(double value);
double RateProfile(double inputValue, double maxRate, double centerSensitivity, double expo);
void MixRCCommands(double xInput, double yInput, double &motorInputs);


// setup runs only once
void setup()
{
    // initialize ports on ESP32
    // ex. ponMode(pin, OUTPUT or INPUT) 
}

// loop will run indefinitely
void loop()
{
    // space for declaring/ initializing variables and constants
    double *motorInputs[2]; // motorInputs[0] - left motor, motorInputs[1] - right motor


    // 1. Get control data from AlfredoCRSF

    // 2. Basic Control Logic: if (armed), if radio connected, etc

    // 3. Call Normalize Value on the X and Y stick inputs for drive

    // 4. Send Inputs to MixRCCommands

    // 5. Apply Rate Profile to the motor inputs
    
    // 6. Send motor inputs to AlfredoDSHOT
    
}

// Custom functions below this line -------------------------------------------------

double NormalizeValue(double value)
{
    /*
    Forces a double into a range [1000.0, 2000.0]
    Then puts the value into a range of [0.0, 100.0]
    */

    // Forces a double into a range [1000.0, 2000.0]
    if (value < 1000)
    {
        value = 1000;
    }
    if (value > 2000)
    {
        value = 2000;
    }

    // Puts the value into a range of [0.0, 100.0]
    value = (value - 1000) / 10;
    
    return value;
}

double RateProfile(double inputValue, double maxRate, double centerSensitivity, double expo)
{
    /*
    Applies a rate profile to an input value.
    Args:
        inputValue: input value range [0.0, 100.0]
    Returns:
        output in range [0.0, 100.0]

    Function:
    https://www.desmos.com/calculator/xuywkbmlsd
    y=C*x+(M-C)*abs(x)*(E*x^5+(1-E)*x)
    */
    double expoMult;
    double output;

    // keeps value of expo in range [0.0, 1.0]
    if((expo < 0) || (expo > 1)) {
        if(expo < 0) {
            expo = 0;
        }
        if(expo > 1) {
            expo = 1;
        }
    }

    // keeps value of maxRate, inputValue, and centerSensitivity in range [0.0, 100.0]
    if((maxRate < 0) || (maxRate > 100)) {
        if(maxRate < 0) {
            maxRate = 0;
        }
        if(maxRate > 100) {
            maxRate = 100;
        }
    }
    if((inputValue < 0) || (inputValue > 100)) {
        if (inputValue < 0) {
            inputValue = 0;
        }
        if (inputValue > 100) {
            inputValue = 100;
        }
    }
    if((centerSensitivity < 0) || (centerSensitivity > 100)) {
        if (centerSensitivity < 0) {
            centerSensitivity = 0;
        }
        if (centerSensitivity > 100) {
            centerSensitivity = 100;
        }
    }

    // Transforms input to be in range of [-1.0, 1.0]
    inputValue = (inputValue - 50) / 50;
    
    expoMult = (expo * pow(inputValue,5) + (1-expo)*inputValue);
    output = (centerSensitivity* inputValue) +(maxRate - centerSensitivity)*abs(inputValue)*expoMult;

    return output;
}

void MixRCCommands(double xInput, double yInput, double &motorInputs) {
    /*
    x/yInput range: [0.0, 100.0]
    Mapping:
        (0, 0) - bottom left corner and (100, 100) - top right corner
        (0, 0) - bottom middle/straight backwards and (100, 100) - top middle/straight forwards
    */
}