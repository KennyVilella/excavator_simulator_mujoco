/*
This file implements the main functions of the plugin.

Copyright, 2023, Vilella Kenny.
*/
#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <mujoco/mjplugin.h>
#include <mujoco/mujoco.h>
#include "plugin/soil/soil.h"

namespace mujoco::plugin::soil {

// Creates a Soil instance
Soil* Soil::Create(const mjModel* m, mjData* d, int instance) {
    return nullptr;
}

// Plugin constructor
Soil::Soil(const mjModel* m, mjData* d, int instance) {
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

  // Register the plugin
  mjp_registerPlugin(&plugin);
}

}  // namespace mujoco::plugin::soil
