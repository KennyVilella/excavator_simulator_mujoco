#ifndef MUJOCO_PLUGIN_SOIL_H_
#define MUJOCO_PLUGIN_SOIL_H_

#include <optional>

#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <mujoco/mujoco.h>

namespace mujoco::plugin::soil {

class Soil {
 public:
  // Creates a new Soil instance or returns null on failure.
  static std::optional<Soil> Create(const mjModel* m, mjData* d, int instance);
  Soil(Soil&&) = default;
  ~Soil() = default;

  static void RegisterPlugin();

 private:
  Soil(const mjModel* m, mjData* d, int instance);
};

}  // namespace mujoco::plugin::soil

#endif  // MUJOCO_PLUGIN_SOIL_H_
