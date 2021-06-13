# Modifying Project X firmware

As the project is quite demanding, it is recommended to precompile micropython scripts into frozen bytecode. The following chapters describe one way of doing it.

# Environmental setup

1. Install any linux distribution (Ubuntu 20.04.2 LTS on a virtual machine is used in this example)
2. Copy .sh scripts located in this directory into user's home directory.
3. Install ESP open SDK using provided script:

```bash
./01_setup_sdk.sh
```

4. Install newest version of micropython (v1.14 is used in this example):

```bash
# on first run, open the script and change your local user path
./02_setup_micropython.sh
```

# Compiling the project

1. After modifying the sources, copy all contents of ```../sources``` directory directly to ```/home/USERNAME/micropython/ports/esp8266```
2. Compile the sources:

```bash
# on first run, open the script and change your local user path
# also, change location of the output folder to which the binaries will be copies (in this example it is /media/sf_shared/outputs/, which is synchronized with my main machine)
./03_recompile.sh
```
3. On the main machine, reload the binary to ESP8266, as presented in project's README.