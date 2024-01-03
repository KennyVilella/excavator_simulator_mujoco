"""Generates an excavator model.

The purpose of the functions in this file is to generate an excavator model provided
its pose, the geometry of the soil grid, and the properties of the soil simulator.
All the properties are given to the function as a dictionary.
The model generation relies on Jinja.

The generated model is written in the excavator folder and is named
"generated_model.xml".

Typical usage example:

    from model_generation import generate_excavator_model
    generate_excavator_model(excavator_model)

Copyright, 2023,  Vilella Kenny.
"""
import numpy as np
import os
from jinja2 import Environment, FileSystemLoader
from pose_calculation import _calc_excavator_pose


# ==================================================================================== #
#                                                                                      #
#          Starting implementation of functions to generate an excavator model         #
#                                                                                      #
# ==================================================================================== #
def generate_excavator_model(excavator_model: dict) -> list:
    """Generates an excavator model.

    This function generates an excavator model following the properties inside the
    input dictionary.

    As the convention between MuJoCo and the pose calculation script is slightly
    different, some conversion has to be made. In particular, all distances are
    converted into meters and all angles in degrees, angles are defined as positive
    counter clockwise in the pose calculation script while MuJoCo follows the opposite
    convention.

    Note that a second dictionary is used in order to not modify the properties inside
    the input dictionary.

    The generated model is written into the model/excavator folder under the
    "generated_moedl.xml" name.

    Args:
        model_excavator: Dictionary gathering all information about the excavator model.
                         It contains:
            soil: Dictionary gathering all information about the soil plugin.
                  It contains:
                grid_length_x: Total length of the grid in the X direction. [m]
                               Default value to 8.0.
                grid_length_y: Total length of the grid in the Y direction. [m]
                               Default value to 8.0.
                grid_length_z: Total length of the grid in the Z direction. [m]
                               Default value to 12.0.
                cell_size_xy: Length of the grid cells in the horizontal direction. [m]
                              Default value to 0.025.
                cell_size_z: Height of the grid cells. Default value to 0.05. [m]
                repose_angle: Repose angle. Default value to 0.85. [rad]
                max_iterations: Maximum number of iteration for the soil relaxation.
                                Default value to 10.
                cell_buffer: Number of cell used as a buffer around the active zone.
                             Default value to 4.
                amp_noise: Amplitude of the noise used for the terrain initialization.
                           Default value to 50.0.
            pose: Dictionary gathering all information about the excavator pose.
                  It contains:
                angle_boom: Angle of the boom relative to the horizontal plane. [deg]
                            Default value to 30.0.
                angle_arm: Angle of the arm relative to the horizontal plane. [deg]
                           Default value to -30.0.
                angle_bucket: Angle of the bucket relative to the horizontal [deg]
                              plane. Default value to 40.0.
    """
    # Creating a new empty dictionary to avoid changing the input
    processed_excavator_model = {}
    processed_excavator_model["soil"] = {}
    processed_excavator_model["pose"] = {}

    # Populating the soil dictionary
    processed_excavator_model["soil"]["grid_length_x"] = excavator_model["soil"].get(
        "grid_length_x", 8.0)
    processed_excavator_model["soil"]["grid_length_y"] = excavator_model["soil"].get(
        "grid_length_y", 8.0)
    processed_excavator_model["soil"]["grid_length_z"] = excavator_model["soil"].get(
        "grid_length_z", 12.0)
    processed_excavator_model["soil"]["grid_size_x"] = round(
        processed_excavator_model["soil"]["grid_length_x"] /
        excavator_model["soil"].get("cell_size_xy", 0.025))
    processed_excavator_model["soil"]["grid_size_y"] = round(
        processed_excavator_model["soil"]["grid_length_y"] /
        excavator_model["soil"].get("cell_size_xy", 0.025))
    processed_excavator_model["soil"]["cell_size_z"] = excavator_model["soil"].get(
        "cell_size_z", 0.05)
    processed_excavator_model["soil"]["repose_angle"] = excavator_model["soil"].get(
        "repose_angle", 0.85)
    processed_excavator_model["soil"]["max_iterations"] = excavator_model["soil"].get(
        "max_iterations", 10)
    processed_excavator_model["soil"]["cell_buffer"] = excavator_model["soil"].get(
        "cell_buffer", 4)
    processed_excavator_model["soil"]["amp_noise"] = excavator_model["soil"].get(
        "amp_noise", 50.0)

    # Calculating the excavator pose
    angle_boom = excavator_model["pose"].get("angle_boom", 30.0)
    angle_arm = excavator_model["pose"].get("angle_arm", -30.0)
    angle_bucket = excavator_model["pose"].get("angle_bucket", 40.0)
    [
        angle_cb_piston, ext_cb_piston, x_I, z_I, angle_ba_piston, ext_ba_piston,
        angle_ah_piston, ext_ah_piston, angle_h_link, x_M, z_M, x_L, z_L,
        angle_side_link
    ] = _calc_excavator_pose(
        np.deg2rad(angle_boom), np.deg2rad(angle_arm), np.deg2rad(angle_bucket))

    # Calculating total angles in degrees
    angle_arm_rad = -np.deg2rad(angle_arm)
    angle_bucket_rad = -np.deg2rad(angle_bucket) + angle_arm_rad

    # Calculating bucket reference orientation
    bucket_quat_w = np.cos(angle_arm_rad / 2)
    bucket_quat_y = np.sin(angle_arm_rad / 2)

    # Calculating coordinate of arm/bucket attachment point in arm reference frame
    x_I_arm = x_I * np.cos(angle_arm_rad) - z_I * np.sin(angle_arm_rad)
    z_I_arm = x_I * np.sin(angle_arm_rad) + z_I * np.cos(angle_arm_rad)

    # Calculating coordinate of bucket attachment point in arm reference frame
    x_M_arm = x_M * np.cos(angle_arm_rad) - z_M * np.sin(angle_arm_rad)
    z_M_arm = x_M * np.sin(angle_arm_rad) + z_M * np.cos(angle_arm_rad)

    # Calculating coordinate of side link attachment point in bucket reference frame
    x_L_bucket = x_L * np.cos(angle_bucket_rad) - z_L * np.sin(angle_bucket_rad)
    z_L_bucket = x_L * np.sin(angle_bucket_rad) + z_L * np.cos(angle_bucket_rad)

    # Converting angles from radians to degrees
    angle_cb_piston = np.rad2deg(angle_cb_piston)
    angle_ba_piston = np.rad2deg(angle_ba_piston)
    angle_ah_piston = np.rad2deg(angle_ah_piston)
    angle_h_link = np.rad2deg(angle_h_link)
    angle_side_link = np.rad2deg(angle_side_link)

    # Converting distances from cm to m
    ext_cb_piston = ext_cb_piston / 100.0
    ext_ba_piston = ext_ba_piston / 100.0
    ext_ah_piston = ext_ah_piston / 100.0
    x_I_arm = x_I_arm / 100.0
    z_I_arm = z_I_arm / 100.0
    x_M_arm = x_M_arm / 100.0
    z_M_arm = z_M_arm / 100.0
    x_L_bucket = x_L_bucket / 100.0
    z_L_bucket = z_L_bucket / 100.0

    # Testing validity of requested pose
    if (ext_cb_piston > 0.56):
        raise Exception(
            "Excavator pose invalid.\n Chassis/boom piston extension is too large.")
    if (ext_cb_piston < 0.06):
        raise Exception(
            "Excavator pose invalid.\n Chassis/boom piston extension is too short.")
    if (ext_ba_piston > 1.1):
        raise Exception(
            "Excavator pose invalid.\n Boom/arm piston extension is too large.")
    if (ext_ba_piston < 0.28):
        raise Exception(
            "Excavator pose invalid.\n Boom/arm piston extension is too short.")
    if (ext_ah_piston > 0.75):
        raise Exception(
            "Excavator pose invalid.\n Arm/bucket piston extension is too large.")
    if (ext_ah_piston < 0.15):
        raise Exception(
            "Excavator pose invalid.\n Arm/bucket piston extension is too short.")

    # Populating the pose dictionary
    processed_excavator_model["pose"]["angle_boom"] = -angle_boom
    processed_excavator_model["pose"]["angle_arm"] = -angle_arm + angle_boom
    processed_excavator_model["pose"]["angle_bucket"] = -angle_bucket
    processed_excavator_model["pose"]["bucket_quat_w"] = bucket_quat_w
    processed_excavator_model["pose"]["bucket_quat_y"] = bucket_quat_y
    processed_excavator_model["pose"]["angle_chassis_boom_piston"] = angle_cb_piston
    processed_excavator_model["pose"]["ext_chassis_boom_piston"] = ext_cb_piston
    processed_excavator_model["pose"]["angle_boom_arm_piston"] = angle_ba_piston
    processed_excavator_model["pose"]["ext_boom_arm_piston"] = ext_ba_piston
    processed_excavator_model["pose"]["x_arm_bucket_piston"] = x_I_arm
    processed_excavator_model["pose"]["z_arm_bucket_piston"] = z_I_arm
    processed_excavator_model["pose"]["angle_arm_bucket_piston"] = angle_ah_piston
    processed_excavator_model["pose"]["ext_arm_bucket_piston"] = ext_ah_piston
    processed_excavator_model["pose"]["angle_h_link"] = angle_h_link
    processed_excavator_model["pose"]["x_bucket"] = x_M_arm
    processed_excavator_model["pose"]["z_bucket"] = z_M_arm
    processed_excavator_model["pose"]["x_side_link"] = x_L_bucket
    processed_excavator_model["pose"]["z_side_link"] = z_L_bucket
    processed_excavator_model["pose"]["angle_side_link"] = angle_side_link

    # Generating excavator model
    filepath = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(filepath, "..", "template")
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    model_template = env.get_template("excavator.xml")
    generated_model = model_template.render(processed_excavator_model)

    # Writing generated model to file
    model_path = os.path.join(filepath, "..")
    filename = model_path + "/generated_excavator.xml"
    with open(filename, "w") as model:
        model.write(generated_model)


if __name__ == "__main__":
    # Creating dictionary to generate an excavator model
    soil = {
        "grid_length_x": 8.0,
        "grid_length_y": 8.0,
        "grid_length_z": 12.0,
        "cell_size_xy": 0.025,
        "cell_size_z": 0.05,
        "repose_angle": 0.85,
        "max_iterations": 10,
        "cell_buffer": 4,
        "amp_noise": 50.0,
    }
    pose = {
        "angle_boom": 50.0,
        "angle_arm": -20.0,
        "angle_bucket": 30.0,
    }
    excavator_model = {
        "soil": soil,
        "pose": pose,
    }

    # Generating excavator model
    generate_excavator_model(excavator_model)
