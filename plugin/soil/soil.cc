/*
This file implements the main functions of the plugin.

Copyright, 2023, Vilella Kenny.
*/

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <sstream>
#include <iostream>
#include <optional>
#include <string>
#include <utility>
#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <mujoco/mjplugin.h>
#include <mujoco/mujoco.h>
#include "soil.h"
#include <soil_simulator/soil_dynamics.hpp>
#include <soil_simulator/types.hpp>

namespace mujoco::plugin::soil {
namespace {

// Check that input parameter is present
bool CheckAttr(const char* name, const mjModel* m, int instance) {
  char *end;
  std::string value = mj_getPluginConfig(m, instance, name);
  value.erase(std::remove_if(value.begin(), value.end(), isspace), value.end());
  strtod(value.c_str(), &end);
  return end == value.data() + value.size();
}

}

// Creates a Soil instance
Soil* Soil::Create(const mjModel* m, mjData* d, int instance) {
    // Checking all input parameters
    if (!CheckAttr("cell_size_z", m, instance))
        mju_error("Soil plugin: Invalid ``cell_size_z`` parameter specification");
    if (!CheckAttr("repose_angle", m, instance))
        mju_error("Soil plugin: Invalid ``repose_angle`` parameter specification");
    if (!CheckAttr("max_iterations", m, instance))
        mju_error("Soil plugin: Invalid ``max_iterations`` parameter specification");
    if (!CheckAttr("cell_buffer", m, instance))
        mju_error("Soil plugin: Invalid ``cell_buffer`` parameter specification");

    return new Soil(m, d, instance);
}

// Plugin constructor
Soil::Soil(const mjModel* m, mjData* d, int instance) {
    // Importing all input parameters
    mjtNum cell_size_z = strtod(mj_getPluginConfig(m, instance, "cell_size_z"), nullptr);
    mjtNum repose_angle = strtod(mj_getPluginConfig(m, instance, "repose_angle"), nullptr);
    mjtNum max_iterations = strtod(mj_getPluginConfig(m, instance, "max_iterations"), nullptr);
    mjtNum cell_buffer = strtod(mj_getPluginConfig(m, instance, "cell_buffer"), nullptr);

    // Calculating geometry of the grid
    int* length_x = m->hfield_nrow;
    int* length_y = m->hfield_ncol;
    mjtNum grid_size_x = m->hfield_size[0];
    mjtNum grid_size_y = m->hfield_size[1];
    mjtNum grid_size_z = m->hfield_size[2];
    mjtNum cell_size_xy = 2.0 * grid_size_x / *length_x;

    // Initalizing the simulator
    soil_simulator::SoilDynamics sim;

    // Initalizing the simulation grid
    soil_simulator::Grid grid(
        grid_size_x, grid_size_y, grid_size_z, cell_size_xy, cell_size_z);

    // Initalizing the simulated bucket
    std::vector<float> o_pos_init = {0.0, 0.0, 0.0};
    std::vector<float> j_pos_init = {0.0, 0.0, 0.0};
    std::vector<float> b_pos_init = {0.0, 0.0, -0.5};
    std::vector<float> t_pos_init = {0.7, 0.0, -0.5};
    float bucket_width = 0.5;
    soil_simulator::Bucket *bucket = new soil_simulator::Bucket(
        o_pos_init, j_pos_init, b_pos_init, t_pos_init, bucket_width);

    // Initalizing the simulation parameter
    soil_simulator::SimParam sim_param(repose_angle, max_iterations, cell_buffer);

    // Initalizing the simulation outputs class
    soil_simulator::SimOut *sim_out = new soil_simulator::SimOut(grid);
}

// Plugin compute
void Soil::Compute(const mjModel* m, mjData* d, int instance) {
}

// Plugin registration
void Soil::RegisterPlugin() {
    mjpPlugin plugin;
    mjp_defaultPlugin(&plugin);

    plugin.name = "mujoco.soil";
    plugin.capabilityflags |= mjPLUGIN_PASSIVE;

    // Input parameters
    const char* attributes[] = {"cell_size_z", "repose_angle", "max_iterations", "cell_buffer"};
    plugin.nattribute = sizeof(attributes) / sizeof(attributes[0]);
    plugin.attributes = attributes;

    // Stateless
    plugin.nstate = +[](const mjModel* m, int instance) { return 0; };

    // Initialization callback
    plugin.init = +[](const mjModel* m, mjData* d, int instance) {
        auto* Soil = Soil::Create(m, d, instance);
        if (!Soil) {
            return -1;
        }
        d->plugin_data[instance] = reinterpret_cast<uintptr_t>(Soil);
        return 0;
    };

    // Destruction callback
    plugin.destroy = +[](mjData* d, int instance) {
        delete reinterpret_cast<Soil*>(d->plugin_data[instance]);
        d->plugin_data[instance] = 0;
    };

    // Compute callback
    plugin.compute =
        +[](const mjModel* m, mjData* d, int instance, int capability_bit) {
            auto* Soil =
                reinterpret_cast<class Soil*>(d->plugin_data[instance]);
            Soil->Compute(m, d, instance);
        };

    // Register the plugin
    mjp_registerPlugin(&plugin);
}

}  // namespace mujoco::plugin::soil
