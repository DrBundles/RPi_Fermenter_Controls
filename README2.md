# Initial Setup
* Plug everything in and start up. Select Jessie Pixel from NOOBS. Takes awhile to initialize. 

  ```
  $ sudo apt-get update
  $ sudo apt-get upgrade
  $ sudo rpi-upgrade
  ```

* If your screen is too large / too small for the display
  * [Troubleshoot screen size](http://stackoverflow.com/questions/22891235/how-to-change-screen-resolution-of-raspberry-pi)
  * [RPi configuration](http://elinux.org/RPiconfig)
  * sudo vi /boot/config.txt
  
    ```
    overscan_left=230
    overscan_right=230
    overscan_top=10
    overscan_bottom=10 
    ```
# Install git
```
$ sudo apt-get install git
$ git config --global user.name "John Doe"
$ git config --global user.email johndoe@example.com
```

# Install vim and vim packages
* Install vim 

  ```
  $ sudo apt-get install vim
  ```

# Install python packages
* Install matplotlib

  ```
  $ sudo pip3 install matplotlib
  ```

# Install RPi.GPIO
Already installed on RPi python3 distribution

# Install W1ThermSensor
* From their [website][w1therm]. Better instructions from Adafruit [here][ada_therm]


* Check if there are any temp sensors with `ls -l /sys/bus/w1/devices/`

* Edit `/boot/config.txt`
* Add the line 'dtoverlay=w1-gpio'
* Reboot the Pi

    ```
    $sudo modprobe w1-gpio
    $sudo modprobe w1-therm
    ```


# Install virtualenvwrapper for python
* [Tutorial](http://www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/) See step 7
* Install virtualenv and virtualenvwrapper

  ```
  $ sudo pip install virtualenv virtualenvwrapper
  $ sudo rm -rf ~/.cache/pip
  ```
* Update your ~/.profile
  
  ```
  # virtualenv and virtualenvwrapper
  export WORKON_HOME=$HOME/.virtualenvs
  source /usr/local/bin/virtualenvwrapper.sh
  ```
* Reload your .profile
  
  ```
  $ source ~/.profile
  ```
* Create a virtual environment for python 3 development
    * which python3 #Output: /usr/bin/python3
    * mkvirtualenv --python=/usr/bin/python3 nameOfEnvironment
    
      ```
      $ mkvirtualenv --python=/usr/bin/python3 py3_general
      ```
* Get out of "py3_general" environment and create a virtual environment for python 2 development

    ```
    $ deactivate
    $ mkvirtualenv py2_general
    ```
* Notice that "(py2_general)" is prepended to your command line, this tells you which virtual environment you are currently working in. To get out of the current virtual environment.

  ```
  $ deactivate
  ```
* To see what virtual environments are installed
  
  ```
  $ lsvirtualenv
  ```
* When you first boot the computer ane open terminal reload the source to be able to use virtualenv commands

  ```
  $ source ~/.profile
  ```
* To load a virtual environment into the terminal 

  ```
  $ workon py3_general
  ```
# Setup python 3 virtual environment
* Open python environment and add required libraries

    ```
    $ source ~/.profile
    $ workon py3_general
    $ pip -V
    $ 
    ```

# Install gpio command line interface
* Install wiringpi gpio interface

  ```
  $ git clone git://git.drogon.net/wiringPi
  $ cd wiringPi
  $ ./build
  ```
* WiringPi [gpio pinout](http://wiringpi.com/pins/) and [commands](http://wiringpi.com/the-gpio-utility/)


# Setup PiTFT+
* Website detailing hardware [installation](https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi).
* Install adafruit [PiTFT Kernel](https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install).
  
  ```
  $ curl -SLs https://apt.adafruit.com/add-pin | sudo bash
  $ sudo apt-get install -y raspberrypi-bootloader adafruit-pitft-helper raspberrypi-kernel
  ```
* Enable and configure PiTFT, 35r is for the 3.5" PiTFT
  
  ```
  $ sudo adafruit-pitft-helper -t 35r
  ```
* To [switch between](https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/faq) HDMI and PiTFT, edit (add if necesseary) the file **/usr/share/X11/xorg.conf.d/99-fbdev.conf**. [Also helpful](https://github.com/notro/fbtft/wiki/Framebuffer-use)
  
  ```
  Section "Device"
    Identifier "display"
     Driver "fbdev"
     Option "fbdev" "/dev/fb0"
  EndSection
  ```
# OpenScale Setup Load Cell
* Learn how to hook up [OpenScale](https://learn.sparkfun.com/tutorials/openscale-applications-and-hookup-guide?_ga=1.265964685.306549472.1478204359)
* 



[w1therm]:https://github.com/timofurrer/w1thermsensor
[ada_therm]:https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20
