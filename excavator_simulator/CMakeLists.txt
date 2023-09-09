# This file has been partially copied and modified from the mujoco repository (deepmind).
# The original license is provided below.
#
# Copyright 2021 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Build simulate executable
if(APPLE)
    set(SIMULATE_RESOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../dist/mujoco.icns)
elseif(WIN32)
    set(SIMULATE_RESOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../dist/simulate.rc)
else()
    set(SIMULATE_RESOURCE_FILES "")
endif()

add_executable(excavator_simulator main.cc)
target_compile_options(excavator_simulator PUBLIC ${MUJOCO_SIMULATE_COMPILE_OPTIONS})
if(WIN32)
    add_custom_command(
        TARGET excavator_simulator
        PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/../dist/mujoco.ico
                ${CMAKE_CURRENT_SOURCE_DIR}
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E rm ${CMAKE_CURRENT_SOURCE_DIR}/mujoco.ico
    )
endif()

target_link_libraries(
    excavator_simulator
    libsimulate
    mujoco::mujoco
    glfw
    Threads::Threads
    lodepng
)

target_link_options(excavator_simulator PRIVATE ${MUJOCO_SIMULATE_LINK_OPTIONS})
