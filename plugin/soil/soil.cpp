#include <mujoco/mjplugin.h>
#include <mujoco/mujoco.h>
#include "soil.hpp"

namespace mujoco::plugin::soil {

// Plugin constructor
Soil::Soil(const mjModel* m, mjData* d, int instance) {
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
    auto soil_or_null = Soil::Create(m, d, instance);
    if (!soil_or_null.has_value()) {
      return -1;
    }
    d->plugin_data[instance] = reinterpret_cast<uintptr_t>(
        new Soil(std::move(*soil_or_null)));
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
