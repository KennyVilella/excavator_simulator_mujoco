"""Generates an excavator model.

The purpose of the functions in this file is to generate an excavator model provided
its pose, the geometry of the soil grid, and the properties of the soil simulator.
All the properties are given to the function as a dictionnary.
The model generation relies on Jinja.

Typical usage example:


Copyright, 2023,  Vilella Kenny.
"""
import numpy as np
import os
from jinja2 import Environment, FileSystemLoader
from pose_calculation import _calc_excavator_pose
#======================================================================================#
#                                                                                      #
#          Starting implementation of functions to generate an excavator model         #
#                                                                                      #
#======================================================================================#
def generate_excavator_model(excavator_model: dict) -> list:
    # Creating a new empty dictionary to avoid changing the input
    processed_excavator_model = {}
    processed_excavator_model["soil"] = {}
    processed_excavator_model["pose"] = {}

    # Populating the soil dictionary
    processed_excavator_model["soil"]["grid_length_x"] = excavator_model.get(
        "grid_length_x", 8.0)
    processed_excavator_model["soil"]["grid_length_y"] = excavator_model.get(
        "grid_length_y", 8.0)
    processed_excavator_model["soil"]["grid_length_z"] = excavator_model.get(
        "grid_length_z", 12.0)
    processed_excavator_model["soil"]["grid_size_x"] = round(
        processed_excavator_model["soil"]["grid_length_x"] /
        excavator_model.get("cell_size_xy", 0.025))
    processed_excavator_model["soil"]["grid_size_y"] = round(
        processed_excavator_model["soil"]["grid_length_y"] /
        excavator_model.get("cell_size_xy", 0.025))
    processed_excavator_model["soil"]["cell_size_z"] = excavator_model.get(
        "cell_size_z", 0.05)
    processed_excavator_model["soil"]["repose_angle"] = excavator_model.get(
        "repose_angle", 0.85)
    processed_excavator_model["soil"]["max_iterations"] = excavator_model.get(
        "max_iterations", 10)
    processed_excavator_model["soil"]["cell_buffer"] = excavator_model.get(
        "cell_buffer", 4)
    processed_excavator_model["soil"]["amp_noise"] = excavator_model.get(
        "amp_noise", 50.0)

    # Calculating the excavator pose
    angle_boom = excavator_model.get("angle_boom", 30.0)
    angle_arm = excavator_model.get("angle_arm", -30.0)
    angle_bucket = excavator_model.get("angle_bucket", 40.0)
    [angle_cb_piston, ext_cb_piston, angle_ba_piston, ext_ba_piston, angle_ah_piston,
        ext_ah_piston, angle_h_link, angle_side_link] = _calc_excavator_pose(
        np.deg2rad(angle_boom), np.deg2rad(angle_arm), np.deg2rad(angle_bucket))

    # Converting angles fram radians to degrees
    angle_cb_piston = np.rad2deg(angle_cb_piston)
    angle_ba_piston = np.rad2deg(angle_ba_piston)
    angle_ah_piston = np.rad2deg(angle_ah_piston)
    angle_h_link = np.rad2deg(angle_h_link)
    angle_side_link = np.rad2deg(angle_side_link)

    # Converting distances from cm to m
    ext_cb_piston = ext_cb_piston / 100.0
    ext_ba_piston = ext_ba_piston / 100.0
    ext_ah_piston = ext_ah_piston / 100.0

    # Populating the pose dictionary
    processed_excavator_model["pose"]["angle_boom"] = -angle_boom
    processed_excavator_model["pose"]["angle_arm"] = -angle_arm
    processed_excavator_model["pose"]["angle_bucket"] = -angle_bucket
    processed_excavator_model["pose"]["angle_chassis_boom_piston"] = -angle_cb_piston
    processed_excavator_model["pose"]["ext_chassis_boom_piston"] = ext_cb_piston
    processed_excavator_model["pose"]["angle_boom_arm_piston"] = angle_ba_piston
    processed_excavator_model["pose"]["ext_boom_arm_piston"] = ext_ba_piston
    processed_excavator_model["pose"]["angle_arm_bucket_piston"] = angle_ah_piston
    processed_excavator_model["pose"]["ext_arm_bucket_piston"] = ext_ah_piston
    processed_excavator_model["pose"]["angle_h_link"] = angle_h_link
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
        "angle_boom": 30.0,
        "angle_arm": -30.0,
        "angle_bucket": 40.0,
    }
    excavator_model = {
        "soil": soil,
        "pose": pose,
    }

    # Generating excavator model
    generate_excavator_model(excavator_model)
