/*
This file declares the main functions of the plugin.

Copyright, 2023, Vilella Kenny.
*/
#ifndef PLUGIN_SOIL_SOIL_H_
#define PLUGIN_SOIL_SOIL_H_

#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <optional>
#include <soil_simulator/soil_dynamics.hpp>
#include <soil_simulator/types.hpp>

namespace mujoco::plugin::soil {

class Soil {
 public:
     // Creates a new Dynamics instance or returns null on failure.
     static Soil* Create(const mjModel* m, mjData* d, int instance);
     Soil(Soil&&) = default;
     ~Soil() = default;

     void Compute(const mjModel* m, mjData* d, int instance);

     static void RegisterPlugin();

     int bucket_id;
     int terrain_id;
     soil_simulator::SoilDynamics sim;
     soil_simulator::Grid grid;
     soil_simulator::Bucket bucket;
     soil_simulator::SimParam sim_param;
     soil_simulator::SimOut sim_out;
 private:
     Soil(const mjModel* m, mjData* d, int instance);
};

}  // namespace mujoco::plugin::soil

#endif  // PLUGIN_SOIL_SOIL_H_
