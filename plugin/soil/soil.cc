/*
This file implements the main functions of the plugin.

Copyright, 2023, Vilella Kenny.
*/

#include "soil.h"
#include <mujoco/mjdata.h>
#include <mujoco/mjmodel.h>
#include <mujoco/mjplugin.h>
#include <mujoco/mujoco.h>
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <sstream>
#include <iostream>
#include <optional>
#include <string>
#include <utility>
#include <vector>
#include <soil_simulator/soil_dynamics.hpp>
#include <soil_simulator/types.hpp>
#include <soil_simulator/utils.hpp>

namespace mujoco::plugin::soil {
namespace {

// Check that input parameter is present
bool CheckAttr(const char* name, const mjModel* m, int instance) {
    char *end;
    std::string value = mj_getPluginConfig(m, instance, name);
    value.erase(
        std::remove_if(value.begin(), value.end(), isspace), value.end());
    strtod(value.c_str(), &end);
    return end == value.data() + value.size();
}

}  // namespace

// Creates a Soil instance
Soil* Soil::Create(const mjModel* m, mjData* d, int instance) {
    // Checking all input parameters
    if (!CheckAttr("cell_size_z", m, instance))
        mju_error(
            "Soil plugin: Invalid ``cell_size_z`` parameter specification");
    if (!CheckAttr("repose_angle", m, instance))
        mju_error(
            "Soil plugin: Invalid ``repose_angle`` parameter specification");
    if (!CheckAttr("max_iterations", m, instance))
        mju_error(
            "Soil plugin: Invalid ``max_iterations`` parameter specification");
    if (!CheckAttr("cell_buffer", m, instance))
        mju_error(
            "Soil plugin: Invalid ``cell_buffer`` parameter specification");
    if (!CheckAttr("amp_noise", m, instance))
        mju_error(
            "Soil plugin: Invalid ``amp_noise`` parameter specification");

    // Setting HFields and terrain id
    int bucket_id = mj_name2id(m, mjOBJ_BODY, "bucket");
    int terrain_id = mj_name2id(m, mjOBJ_HFIELD, "terrain");
    int bucket_soil_1_id = mj_name2id(m, mjOBJ_HFIELD, "bucket soil 1");
    int bucket_soil_2_id = mj_name2id(m, mjOBJ_HFIELD, "bucket soil 2");

    // Checking bucket and HField
    if (bucket_id == -1)
        mju_error("Soil plugin: No ``bucket`` has been detected");
    if (terrain_id == -1)
        mju_error("Soil plugin: No ``terrain`` HField has been detected");
    if (bucket_soil_1_id == -1)
        mju_error("Soil plugin: No ``bucket soil 1`` HField has been detected");
    if (bucket_soil_2_id == -1)
        mju_error("Soil plugin: No ``bucket soil 2`` HField has been detected");

    // Checking consistency of HFields
    if (m->hfield_nrow[terrain_id] != m->hfield_nrow[bucket_soil_1_id])
        mju_error("Soil plugin: Inconsistent number of rows between "
            "``terrain`` and ``bucket soil 1`` HFields");
    if (m->hfield_nrow[terrain_id] != m->hfield_nrow[bucket_soil_2_id])
        mju_error("Soil plugin: Inconsistent number of rows between "
            "``terrain`` and ``bucket soil 2`` HFields");
    if (m->hfield_ncol[terrain_id] != m->hfield_ncol[bucket_soil_1_id])
        mju_error("Soil plugin: Inconsistent number of columns between "
            "``terrain`` and ``bucket soil 1`` HFields");
    if (m->hfield_ncol[terrain_id] != m->hfield_ncol[bucket_soil_2_id])
        mju_error("Soil plugin: Inconsistent number of columns between "
            "``terrain`` and ``bucket soil 2`` HFields");
    if (m->hfield_size[4*terrain_id] != m->hfield_size[4*bucket_soil_1_id])
        mju_error("Soil plugin: Inconsistent size in the X direction between "
            "``terrain`` and ``bucket soil 1`` HFields");
    if (m->hfield_size[4*terrain_id] != m->hfield_size[4*bucket_soil_2_id])
        mju_error("Soil plugin: Inconsistent size in the X direction between "
            "``terrain`` and ``bucket soil 2`` HFields");
    if (m->hfield_size[4*terrain_id+1] != m->hfield_size[4*bucket_soil_1_id+1])
        mju_error("Soil plugin: Inconsistent size in the Y direction between "
            "``terrain`` and ``bucket soil 1`` HFields");
    if (m->hfield_size[4*terrain_id+1] != m->hfield_size[4*bucket_soil_2_id+1])
        mju_error("Soil plugin: Inconsistent size in the Y direction between "
            "``terrain`` and ``bucket soil 2`` HFields");
    if (m->hfield_size[4*terrain_id+2] != m->hfield_size[4*bucket_soil_1_id+2])
        mju_error("Soil plugin: Inconsistent size in the Z direction between "
            "``terrain`` and ``bucket soil 1`` HFields");
    if (m->hfield_size[4*terrain_id+2] != m->hfield_size[4*bucket_soil_2_id+2])
        mju_error("Soil plugin: Inconsistent size in the Z direction between "
            "``terrain`` and ``bucket soil 2`` HFields");

    return new Soil(m, d, instance);
}

// Plugin constructor
Soil::Soil(const mjModel* m, mjData* d, int instance) {
    // Importing all input parameters
    mjtNum cell_size_z = strtod(
        mj_getPluginConfig(m, instance, "cell_size_z"), nullptr);
    mjtNum repose_angle = strtod(
        mj_getPluginConfig(m, instance, "repose_angle"), nullptr);
    mjtNum max_iterations = strtod(
        mj_getPluginConfig(m, instance, "max_iterations"), nullptr);
    mjtNum cell_buffer = strtod(
        mj_getPluginConfig(m, instance, "cell_buffer"), nullptr);
    mjtNum amp_noise = strtod(
        mj_getPluginConfig(m, instance, "amp_noise"), nullptr);

    // Determining bucket ID
    bucket_id = mj_name2id(m, mjOBJ_BODY, "bucket");

    // Determining hfield ID of terrain
    terrain_id = mj_name2id(m, mjOBJ_HFIELD, "terrain");

    // Determining hfield ID of bucket soil
    bucket_soil_1_id = mj_name2id(m, mjOBJ_HFIELD, "bucket soil 1");
    bucket_soil_2_id = mj_name2id(m, mjOBJ_HFIELD, "bucket soil 2");

    // Calculating geometry of the grid
    int* length_x = m->hfield_nrow;
    mjtNum grid_size_x = m->hfield_size[0];
    mjtNum grid_size_y = m->hfield_size[1];
    mjtNum grid_size_z = 0.5 * m->hfield_size[2];
    mjtNum cell_size_xy = 2.0 * grid_size_x / *length_x;

    // Initalizing the simulation grid
    grid = soil_simulator::Grid(
        grid_size_x, grid_size_y, grid_size_z, cell_size_xy, cell_size_z);

    // Initalizing the simulated bucket
    std::vector<float> o_pos_init = {0.0, 0.0, 0.0};
    std::vector<float> j_pos_init = {0.0, 0.0, 0.0};
    std::vector<float> b_pos_init = {0.7, 0.0, -0.5};
    std::vector<float> t_pos_init = {-0.14, 0.0, -0.97};
    float bucket_width = 0.68;
    bucket = new soil_simulator::Bucket(
        o_pos_init, j_pos_init, b_pos_init, t_pos_init, bucket_width);

    // Initalizing the simulation parameter
    sim_param = soil_simulator::SimParam(
        repose_angle, max_iterations, cell_buffer);

    // Initalizing the simulation outputs class
    sim_out = new soil_simulator::SimOut(grid);

    // Setting state associated with visual update
    int spec = mjSTATE_PLUGIN;
    int size = mj_stateSize(m, spec);
    std::vector<mjtNum> soil_state(size);
    soil_state[0] = -1.0;
    mj_setState(m, d, soil_state.data(), spec);

    // Setting initial terrain
    sim.Init(sim_out, grid, amp_noise);

    // Setting hfield with initial terrain
    int n_hfield_terrain = (
        m->hfield_nrow[terrain_id] * m->hfield_ncol[terrain_id]);
    for (auto jj = 0; jj < m->hfield_nrow[terrain_id]; jj++) {
        for (auto ii = 0; ii < m->hfield_ncol[terrain_id]; ii++) {
            // Calculating index for the terrain hfield
            int new_index = m->hfield_nrow[terrain_id] * jj + ii;

            // Updating the terrain hfield
            m->hfield_data[new_index] = (
                sim_out->terrain_[ii][jj] / m->hfield_size[2]);
        }
    }
}

// Plugin compute
void Soil::Compute(const mjModel* m, mjData* d, int instance) {
    // Getting bucket position and orientation
    std::vector<float> pos = {
        static_cast<float>(d->xpos[3*bucket_id]),
        static_cast<float>(d->xpos[3*bucket_id+1]),
        static_cast<float>(d->xpos[3*bucket_id+2])};
    std::vector<float> ori = {
        static_cast<float>(d->xquat[4*bucket_id]),
        static_cast<float>(-d->xquat[4*bucket_id+1]),
        static_cast<float>(-d->xquat[4*bucket_id+2]),
        static_cast<float>(-d->xquat[4*bucket_id+3])};

    // Stepping the soil_simulator
    bool soil_update = sim.Step(
        sim_out, pos, ori, grid, bucket, sim_param, 1e-5);

    if (soil_update) {
        // Allowing the visual update of the terrain
        int spec = mjSTATE_PLUGIN;
        int size = mj_stateSize(m, spec);
        std::vector<mjtNum> soil_state(size);
        soil_state[0] = 1.0;
        mj_setState(m, d, soil_state.data(), spec);

        // Updating Hfield with terrain
        // This should be improved
        // At least update only in the relax_area
        int n_hfield_terrain = (
            m->hfield_nrow[terrain_id] * m->hfield_ncol[terrain_id]);
        for (auto jj = 0; jj < m->hfield_nrow[terrain_id]; jj++) {
            for (auto ii = 0; ii < m->hfield_ncol[terrain_id]; ii++) {
                // Calculating index for the terrain hfield
                int new_index = m->hfield_nrow[terrain_id] * jj + ii;

                // Updating the terrain hfield
                m->hfield_data[new_index] = (
                    sim_out->terrain_[ii][jj] / m->hfield_size[2]);

                // Updating the bucket soil 1 hfield if necessary
                if (
                    (sim_out->body_soil_[0][ii][jj] != 0.0) ||
                    (sim_out->body_soil_[1][ii][jj] != 0.0)) {
                    // Updating
                    m->hfield_data[n_hfield_terrain + new_index] = (
                        sim_out->body_soil_[1][ii][jj] / m->hfield_size[2]);
                } else {
                    // Setting to mjMAXVAL, this is a dirty workaround
                    m->hfield_data[n_hfield_terrain + new_index] = mjMAXVAL;
                }

                // Updating the bucket soil 2 hfield if necessary
                if (
                    (sim_out->body_soil_[2][ii][jj] != 0.0) ||
                    (sim_out->body_soil_[3][ii][jj] != 0.0)) {
                    // Updating
                    m->hfield_data[2*n_hfield_terrain + new_index] = (
                        sim_out->body_soil_[3][ii][jj] / m->hfield_size[2]);
                } else {
                    // Setting to mjMAXVAL, this is a dirty workaround
                    m->hfield_data[2*n_hfield_terrain + new_index] = mjMAXVAL;
                }
            }
        }
    }
}

// Plugin registration
void Soil::RegisterPlugin() {
    mjpPlugin plugin;
    mjp_defaultPlugin(&plugin);

    plugin.name = "mujoco.soil";
    plugin.capabilityflags |= mjPLUGIN_PASSIVE;

    // Input parameters
    const char* attributes[] = {
        "cell_size_z", "repose_angle", "max_iterations", "cell_buffer",
        "amp_noise"};
    plugin.nattribute = sizeof(attributes) / sizeof(attributes[0]);
    plugin.attributes = attributes;

    // One state
    plugin.nstate = +[](const mjModel* m, int instance) { return 1; };

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
