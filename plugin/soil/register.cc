/*
This file registers the soil plugin to MuJoCo.

Copyright, 2023, Vilella Kenny.
*/
#include <mujoco/mjplugin.h>
#include "soil.h"

namespace mujoco::plugin::soil {

mjPLUGIN_LIB_INIT { Soil::RegisterPlugin(); }

}  // namespace mujoco::plugin::soil
