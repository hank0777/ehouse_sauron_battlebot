/*
A throwaway file entirely for testing functions
*/
#include<cmath>
#include<iostream>
using namespace std;

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
    // Transforms input to be in range of [-1.0, 1.0]
    inputValue = (inputValue - 50) / 50;


    // keeps value of expo in range [0,1]
    if((expo < 0) || (expo > 1)) {
        if(expo < 0) {
            expo = 0;
        }
        if(expo > 1) {
            expo = 1;
        }
    }

    // keeps value of maxRate, inputValue, and centerSensitivity in range [0,100]
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

    
    expoMult = (expo * pow(inputValue,5) + (1-expo)*inputValue);
    output = (centerSensitivity* inputValue) +(maxRate - centerSensitivity)*abs(inputValue)*expoMult;

    return output;
}

int main(){
    cout << RateProfile(75, 100, 20, 0.5);
}