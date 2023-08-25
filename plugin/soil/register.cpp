#include <mujoco/mjplugin.h>
#include "soil.hpp"

namespace mujoco::plugin::soil {

mjPLUGIN_LIB_INIT { Soil::RegisterPlugin(); }

}  // namespace mujoco::plugin::soil
