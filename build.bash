#!/usr/bin/bash

# Determine the path of the repo
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Move to the repo
cd $SCRIPT_DIR

# Copy the soil simulator if not already present
if [ ! -d "plugin/soil/soil_dynamics_cpp" ]; then
  echo "Cloning soil_dynamics_cpp..."
  cd plugin/soil/
  git clone https://github.com/KennyVilella/soil_dynamics_cpp
  cd $SCRIPT_DIR
else
  cd plugin/soil/soil_dynamics_cpp
  if [ "$(git rev-parse --show-toplevel 2>/dev/null)" = "$(pwd)" ]; then
    echo "soil_dynamics_cpp is already installed, skip"
  else
    echo "Cloning soil_dynamics_cpp..."
    cd ../
    rm -rf soil_dynamics_cpp
    git clone https://github.com/KennyVilella/soil_dynamics_cpp
  fi
  cd $SCRIPT_DIR
fi

# Setup the CMake environment
cmake -S . -B build -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++

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

# Copy the excavator_simulator executable to build/bin
cp build/excavator_simulator/excavator_simulator build/bin
