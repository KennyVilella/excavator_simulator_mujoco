#ifndef MUJOCO_PLUGIN_SOIL_DYNAMICS_H_
#define MUJOCO_PLUGIN_SOIL_DYNAMICS_H_

#include <optional>

#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>

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

#endif  // MUJOCO_PLUGIN_SOIL_DYNAMICS_H_
