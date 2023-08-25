set(MUJOCO_SOIL_SRCS
    soil.cpp
    soil.hpp
    register.cpp
)

add_library(soil SHARED)
target_sources(soil PRIVATE ${MUJOCO_SOIL_SRCS})
target_link_libraries(soil PRIVATE mujoco)
target_compile_options(
  soil
  PRIVATE ${AVX_COMPILE_OPTIONS}
          ${MUJOCO_MACOS_COMPILE_OPTIONS}
          ${EXTRA_COMPILE_OPTIONS}
          ${MUJOCO_CXX_FLAGS}
)
target_link_options(
  soil
  PRIVATE
  ${MUJOCO_MACOS_LINK_OPTIONS}
  ${EXTRA_LINK_OPTIONS}
)

