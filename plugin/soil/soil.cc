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

    return new Soil(m, d, instance);
}

// Plugin constructor
Soil::Soil(const mjModel* m, mjData* d, int instance) {
    // Importing all input parameters
    mjtNum cell_size_z = strtod(mj_getPluginConfig(m, instance, "cell_size_z"), nullptr);

    // Calculating geometry of the grid
    int* length_x = m->hfield_nrow;
    int* length_y = m->hfield_ncol;
    mjtNum grid_size_x = m->hfield_size[0];
    mjtNum grid_size_y = m->hfield_size[1];
    mjtNum grid_size_z = m->hfield_size[2];
    mjtNum cell_size_xy = 2.0 * grid_size_x / *length_x;
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
    const char* attributes[] = {"cell_size_z"};
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
