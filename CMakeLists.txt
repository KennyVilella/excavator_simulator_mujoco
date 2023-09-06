# This file has been modified from the mujoco_mpc repository (deepmind).
# The original license is provided below.
#
# Copyright 2022 DeepMind Technologies Limited
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
cmake_minimum_required(VERSION 3.16)

# INTERPROCEDURAL_OPTIMIZATION is enforced when enabled.
set(CMAKE_POLICY_DEFAULT_CMP0069 NEW)
# Default to GLVND if available.
set(CMAKE_POLICY_DEFAULT_CMP0072 NEW)

# This line has to appear before 'PROJECT' in order to be able to disable incremental linking
set(MSVC_INCREMENTAL_DEFAULT ON)

project(excavator_simulator_mujoco VERSION 0.0.1)

enable_language(C)
enable_language(CXX)

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")

include(FindOrFetch)

find_package(Python)
find_package(Threads REQUIRED)

findorfetch(
  USE_SYSTEM_PACKAGE
  OFF
  PACKAGE_NAME
  mujoco
  LIBRARY_NAME
  mujoco
  GIT_REPO
  https://github.com/deepmind/mujoco.git
  GIT_TAG
  2.3.7
  TARGETS
  mujoco::mujoco
  mujoco::platform_ui_adapter
  EXCLUDE_FROM_ALL
)

add_subdirectory(plugin/soil)
