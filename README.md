This template is meant to be used for development of ESP32 in Platformio with the ESP_IDF framework

# features
## transfer of GIT info to code
Transfer is implemented adding the project to GIT versioning and sticking to the tagging discipline.

Version changes are identified adding a tag  in the standard format ```v0.0.0 COMMENT``` - description is free
tthose info will be transferred to the **GIT_fwInfo** struct and to the comments in the header
## dynamic generation of sdkconfig defaults
sdkconfig.defaults is assembled at pre-compile time by the merge_sdkconfig script based on the build flags defined in platformio.ini for the current build environment.

Use of build blags in the base [env] environment is safe.

The link between the build defines and the fragments is established in the ```merge_sdkconfig.py``` script.

To add a new SDKCONFIG fragment, add the fragment to the ```sdkconfigs``` folder and modify the script adding the relevant info to the```flag_to_fragment``` array.

Watch/test for overlapping of definitions between fragments, examining the output file and the sdkconfig.[envirionment] generated later on.

## transfer of certificate and passwords to the ESP
To enable TSL (used, for instance, by ESP32 to secure comms with MQTT), the server certificate need to be available to ESP32.
Instead of hard coding the certificate in the library, the certificate is loaded from a file  embedded in the firmware at compilation time.
The embedding mechanism is picking the ca.crt file in a  folder defined by a Windows system environment variable
The certificate is stored in the folder  path {*use forward slashes!*} specified in the ```ESP_HEADERS``` environment variable.

This prevents accidental disclosure of such data in GIT versioning and centralized storage of updated credential across all projects in develoment.

