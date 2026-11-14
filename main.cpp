/*
    Controls team PSU Ehouse Combat Robotics
    Hi! Hello! Git is Amazing - Peter
    test test test, hi!! - Tiffany
    test test test test test
*/
using namespace std;

double NormalizeValue(double value);
double ApplyRateProfile(double inputValue, double maxRate, double centerSensitivity, double expo);

// setup runs only once
void setup()
{
}

// loop will run indefinitely
void loop()
{
}

// Custom functions below this line -------------------------------------------------

double NormalizeValue(double value)
{
    /*
    Forces a double into a range 1000.0 - 2000.0
    */
    if (value < 1000)
    {
        value = 1000;
    }
    if (value > 2000)
    {
        value = 2000;
    }
    return value;
}

double ApplyRateProfile(double inputValue, double maxRate, double centerSensitivity, double expo)
{
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