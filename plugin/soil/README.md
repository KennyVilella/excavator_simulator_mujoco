# Soil plugin
This folder contains the soil plugin that serves as an interface to the [soil simulator][soil_dyanmics_cpp].
For more information on the soil simulator, the reader is encouraged to consult the documentation available in its [repository][soil_dyanmics_cpp].
Here, the content of the soil plugin as well as its typical usage would be described.

The properties of the simulated grid are obtained fron the various `HField` present in the model.
Only the height of the cells should be provided as an input parameter (`cell_size_z`) of the plugin.
The terrain is then initialized with some noise using the `Init` function of the soil simulator.
The amplitude of the noise can be set in the plugin instance with the `amp_noise` parameter.
A value of `0` generates a flat terrain, `50` a fairly flat terrain with some random small topography, `200` and above for a more rugged terrain.

Every time the soil is updated, that is the bucket has moved from more than a cell size, the `HField` is also updated which in turn updates the visual.
Lower cell size would therefore create larger `HField` that are updated more frequently, which slow down significantly the simulation.

# Requirements
In the current implementation, several key elements are hardcoded so that the model must satisfy these requirements for the soil plugin to work
- The terrain `HField` must be called `terrain`.
- Two `Hfield` should be added for the bucket soil called `bucket soil 1` and `bucket soil 2`.
- The size of the three `HField` mentionned above should be consistent.
- The bucket dimension and shape are hardcoded. If the user wnats to change the bucket/model used, it is then necessary to update the bucket dimension directly in the soil plugin. 

## Parameter list
The plugin has the following parameters:
- `cell_size_z`: Set the height of the grid cell in meter. Typical value is `0.01`.
- `repose_angle`: Set the repose angle of the soil in radian. Typical value is `0.85`.
- `max_iterations`: Set the maximum number of iteration for the soil relaxation.
   Higher values make the simulation slower but produce a terrain state closer to equilibrium. Typical value is `3`.
- `cell_buffer`: Set the number of cell used as a buffer around the active zone. Higher values make the simulation slower without obvious benefit in most cases. Typical value is `4`.
- `amp_noise`: Set the amplitude of the noise used for the terrain initialization. Typical values ranges from `0` to `300`.

Note that typical values of `cell_size_z` and `max_iterations` are somewhat linked.
Higher values of `cell_size_z` would lead to less frequent soil update, so that a larger value for `max_iterations` should be used to get a terrain closer to equilibrium.

## Usage example
```
  <extension>
    <plugin plugin="mujoco.soil">
      <instance name="terrain">
        <config key="cell_size_z" value="0.01"/>
        <config key="repose_angle" value="0.85"/>
        <config key="max_iterations" value="3"/>
        <config key="cell_buffer" value="4"/>
        <config key="amp_noise" value="50.0"/>
      </instance>
    </plugin>
  </extension>
```

[soil_dyanmics_cpp]: https://github.com/KennyVilella/soil_dynamics_cpp
