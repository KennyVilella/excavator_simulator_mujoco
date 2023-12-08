# excavator_simulator_mujoco
This repository implements a simulator of a hydraulic excavator including soil digging, transportation, and dumping.
The simulator is built on the top of a customized version of [MuJoCo][MuJoCo], available [here][Mujoco2].
The only modification of this customized version is a better visualization of floating soil.

The soil dynamics is modeled using [soil_dyanmics_cpp][soil simulator] and a custom soil plugin serves as an interface with [MuJoCo][MuJoCo].
A description of the soil plugin as well as an usage example is provided [here][soil README].
An excavator model is also included that is thoroughly described in the corresponding [README](model/excavator/README.md).

A customized executable to launch [MuJoCo][MuJoCo] is also provided, as the default executable does not include the update of `HField`.

# Installation
A bash script is provided to make the installation of the simulator easier.
To install the simulator, simply execute the following command
```
bash <path_to_repo>/build.bash
```

This script would:
- (if necessary) clone the [soil_dyanmics_cpp][soil simulator] repository and move it to the appropriate folder.
- Build the simulator with CMake.
- Copy the custom plugin library to the appropriate folder.
- Copy the custom executable to the appropriate folder.

# Running the simulator
To run the simulator, simply execute the following command
```
.<path_to_repo>/build/bin/excavator_simulator <path_to_repo>/model/excavator/excavator.xml
```

A window will open with the hydraulic excavator.
It is suggested to toggle on the "Wireframe" view in the "Rendering" section in order to better visualize the soil.
The hydraulic excavator can be actuated using the four sliders in the "Control" section.

# To-do list
There are several important features that are yet to be implemented.
These include, in order of priority:

- A template to generate excavator model with varying initial position.
- Add options to customize the initial terrain shape.
- Improve the soil plugin. In particular, add more check to ensure the plugin is properly connected.
- Improve the actuation. The excavator should not move when a zero velocity is requested.
- Add reaction force from the soil.

[MuJoCo]: https://mujoco.org/
[MuJoCo2]: https://github.com/KennyVilella/mujoco
[soil simulator]: https://github.com/KennyVilella/soil_dynamics_cpp
[soil README]: plugin/soil/README.md
