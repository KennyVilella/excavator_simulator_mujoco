/*
This file declares the main functions of the plugin.

Copyright, 2023, Vilella Kenny.
*/
#ifndef PLUGIN_SOIL_SOIL_H_
#define PLUGIN_SOIL_SOIL_H_

#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <optional>

namespace mujoco::plugin::soil {

class Soil {
 public:
  // Creates a new Dynamics instance or returns null on failure.
  static Soil* Create(const mjModel* m, mjData* d, int instance);
  Soil(Soil&&) = default;
  ~Soil() = default;

  void Compute(const mjModel* m, mjData* d, int instance);

  static void RegisterPlugin();

 private:
  Soil(const mjModel* m, mjData* d, int instance);
};

}  // namespace mujoco::plugin::soil

#endif  // PLUGIN_SOIL_SOIL_H_
