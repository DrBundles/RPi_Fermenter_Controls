## Install jessie image from adafruit
The Rasperry PiTFT 3.5" Plus Touch screen requires a different kernal. So download the image for that Linux distro from adafruit [website][adafruit_tft] and follow the instructions for burning a new image onto a SD card.

## Setup static ip 


## Find what virtual envitonments are on the RPi
* source ~/.profile
* lsvirtualenv
* workon touch

## RPi.GPIO
* Outside virtual env
* sudo apt-get install python-dev python-rpi.gpio
* Now import RPi.GPIO should work on python ide, but will not yet work in virtual env
* Inside virtual env
* pip install rpi.gpio

## Using Wiring Pi
* man gpio
* wiringpi.com/pins - shows which gpio pin is connected to which WiringPi pin numher
* for gpio pin 23, wiringpi 4

## ivPID submodule
* When you clone clone into an existing project that has submodules you must initialize the local directory and then fetch the project

    ```
    $ git submodule init
    $ git submodule update
    ```
* To import ivPID, add path to PID.py to python 

    ```
    # some_file.py
    import sys
    sys.path.insert(0, '/path/to/application/app/folder')

    import file
    ```

* PID.SetPoint(float) sets the set point that the pid is trying to achieve
* PID.output is the value the pid is using to effect the change required to reach the setpoint
* PID.update(float) is the value of the signal being controlled

## Colorscheme
* color molokai
*



[adafruit_tft]: https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install "Link to Adafruit PiTFT installation documentation"
