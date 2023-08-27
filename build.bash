#!/usr/bin/bash

# Determine the path of the repo
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Move to the repo
cd $SCRIPT_DIR

# Copy the soil simulator if not already present
if [ ! -d "plugin/soil/soil_dynamics_cpp" ]; then
  cd plugin/soil/
  git clone https://github.com/KennyVilella/soil_dynamics_cpp
  cd $SCRIPT_DIR
else
  cd plugin/soil/soil_dynamics_cpp
  if [! "git rev-parse --is-inside-work-tree"]; then
    git clone https://github.com/KennyVilella/soil_dynamics_cpp
  fi
  cd $SCRIPT_DIR
fi

# Setup the CMake environment
cmake -S . -B build -DCMAKE_C_COMPILER=clang-16 -DCMAKE_CXX_COMPILER=clang++-16

# Build the soil plugin
cmake --build build

# Build the MuJoCo executable
cmake --build build --target simulate

# Create the folder for custom plugins if it does not exist
if [ ! -d "build/bin/mujoco_plugin" ]; then
  mkdir build/bin/mujoco_plugin
fi

# Copy the soil library to the custom plugin folder
cp build/plugin/soil/libsoil.so build/bin/mujoco_plugin
