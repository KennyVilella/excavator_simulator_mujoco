"""Calculates pose of an excavator.

The purpose of the functions in this file is to calculate the pose of the different
parts of an excavator provided the boom, arm and bucket angle.
The reasoning behind the calculation is provided in the model readme.

Typical usage example:

    from pose_calculation import _calc_excavator_pose
    [
        angle_cb_piston, ext_cb_piston, x_I, z_I, angle_ba_piston, ext_ba_piston,
        angle_ah_piston, ext_ah_piston, angle_h_link, x_M, z_M, x_L, z_L,
        angle_side_link
    ] = _calc_excavator_pose(0.5, 0.0, 0.2)

Copyright, 2023,  Vilella Kenny.
"""
import numpy as np


# ==================================================================================== #
#                                                                                      #
#       Starting implementation of functions used to calculate the excavator pose      #
#                                                                                      #
# ==================================================================================== #
def _calc_excavator_pose(
        angle_boom: float, angle_arm: float, angle_bucket: float) -> list:
    """Calculates the excavator pose.

    This function calculates all the properties required to set the excavator pose in
    the MuJoCo model and prints them.

    The reasoning behind the calculation as well as the convention used are available in
    the model readme.

    Args:
        angle_boom: Angle of the boom relative to the horizontal plane. [rad]
        angle_arm: Angle of the arm relative to the horizontal plane. [rad]
        angle_bucket: Angle of the bucket relative to the horizontal plane. [rad]

    Returns:
        A list containing the angle of the chassis/boom piston relative to the
        horizontal plane, the position of the piston rod in the chassis/boom piston
        cylinder, the position of the arm/bucket piston cylinder attachment in the arm
        frame (X and Z direction), the angle of the boom/arm piston relative to the
        horizontal plane, the position of the piston rod in the boom/arm piston
        cylinder, the angle of the arm/bucket piston relative to the HM segment,
        the position of the piston rod in the arm/bucket piston cylinder, the angle of
        the H link relative to the IJ segment, the position of the bucket attachment in
        the arm frame (X and Z direction), the position of the side link attachment in
        the bucket frame (X and Z direction), and the angle of the side link relative to
        the LM segment.
    """
    # Calculating the pose of the boom
    x_F, z_F, ext_cb_piston, angle_cb_piston = _calc_boom_pose(angle_boom)
    print("\n================= Boom pose =================")
    print("Piston extension: %.2f" % (ext_cb_piston))
    print("angle_chassis_boom_piston: %.2f deg" % (np.rad2deg(angle_cb_piston)))

    # Calculating the pose of the arm
    x_I, z_I, x_K, z_K, x_M, z_M, ext_ba_piston, angle_ba_piston = _calc_arm_pose(
        angle_arm, x_F, z_F)
    angle_ba_piston = angle_boom - angle_ba_piston
    print("\n================= Arm pose =================")
    print("Piston extension: %.2f" % (ext_ba_piston))
    print("angle_boom_arm_piston: %.2f deg" % (np.rad2deg(angle_ba_piston)))

    # Calculating the pose of the H link and bucket
    ext_ah_piston, angle_h_link, angle_ah_piston, x_L, z_L, angle_side_link = (
        _calc_H_link_pose(angle_bucket, x_I, z_I, x_K, z_K, x_M, z_M))
    angle_ah_piston = angle_arm - angle_ah_piston
    angle_side_link = angle_arm + angle_bucket + angle_side_link
    print("\n================= H link pose =================")
    print("Piston extension: %.2f" % (ext_ah_piston))
    print("angle_arm_h_link_piston: %.2f deg" % (np.rad2deg(angle_ah_piston)))
    print("angle_h_link: %.2f deg" % (np.rad2deg(angle_h_link)))
    print("angle_side_link: %.2f deg" % (np.rad2deg(angle_side_link)))

    return [
        angle_cb_piston, ext_cb_piston, x_I, z_I, angle_ba_piston, ext_ba_piston,
        angle_ah_piston, ext_ah_piston, angle_h_link, x_M, z_M, x_L, z_L,
        angle_side_link
    ]


def _calc_boom_pose(angle_boom: float) -> list:
    """Calculates the boom pose.

    This function calculates all the properties required to set the boom in the
    MuJoCo model.

    Some information about this function:
    - All distances are given in cm.
    - All angles are given in radian.
    - The position of E, D, H and F are given in the boom frame.

    The reasoning behind the calculation as well as the convention used are available in
    the model readme.

    Args:
        angle_boom: Angle of the boom relative to the horizontal plane. [rad]

    Returns:
        A list containing the position of the boom/arm piston cylinder attachment in the
        arm frame (X and Z direction), the position of the piston rod in the
        chassis/boom piston cylinder, and the angle of the chassis/boom piston relative
        to the horizontal plane.
    """
    # Input parameters measured from meshes
    CH = 384.5
    CE = 167.8
    CF = 236.2
    piston_cylinder_length = 133.6
    x_D = 47.4
    z_D = -23.7
    angle_HCE = 0.421
    angle_HCF = 0.411

    # Calculating position of the chassis/boom piston rod attachment in the boom frame
    x_E = CE * np.cos(angle_boom + angle_HCE)
    z_E = CE * np.sin(angle_boom + angle_HCE)

    # Calculating position of the arm attachment in the boom frame
    x_H = CH * np.cos(angle_boom)
    z_H = CH * np.sin(angle_boom)

    # Calculating position of the boom/arm piston cylinder attachment in the boom frame
    x_F = CF * np.cos(angle_boom + angle_HCF)
    z_F = CF * np.sin(angle_boom + angle_HCF)

    # Calculating total length of the chassis/boom piston
    ED = np.sqrt((x_E - x_D)**2 + (z_E - z_D)**2)

    # Calculating angle of the chassis/boom piston relative to the horizontal plane
    angle_cb_piston = -np.arccos((x_E - x_D) / ED)

    return [x_F - x_H, z_F - z_H, ED - piston_cylinder_length, angle_cb_piston]


def _calc_arm_pose(angle_arm: float, x_F: float, z_F: float) -> list:
    """Calculates the arm pose.

    This function calculates all the properties required to set the arm in the
    MuJoCo model.

    Some information about this function:
    - All distances are given in cm.
    - All angles are given in radian.
    - The position of G, I, K and M are given in the arm frame.

    The reasoning behind the calculation as well as the convention used are available in
    the model readme.

    Args:
        angle_arm: Angle of the arm relative to the horizontal plane. [rad]
        x_F: Position of the boom/arm piston cylinder attachment in the X direction
             given in the arm frame. [cm]
        z_F: Position of the boom/arm piston cylinder attachment in the Z direction
             given in the arm frame. [cm]

    Returns:
        A list containing the position of the arm/bucket piston cylinder attachment in
        the arm frame (X and Z direction), the position of the H link attachment in the
        arm frame (X and Z direction), the position of the bucket attachment in the arm
        frame (X and Z direction), the position of the piston rod in the boom/arm
        piston cylinder, and the angle of the boom/arm piston relative to the
        horizontal plane.
    """
    # Input parameters measured from meshes
    HG = 57.0
    HM = 199.6
    HI = 44.8
    HK = 152.3
    piston_cylinder_length = 114.7
    angle_GHM = 2.881
    angle_GHI = 1.876
    angle_GHK = 2.838

    # Calculating angle of the segment HG relative to the vertical plane
    alpha = angle_GHM + angle_arm - np.pi / 2

    # Calculating angle of the segment HI relative to the horizontal plane
    beta = angle_GHM + angle_arm - angle_GHI

    # Calculating angle of the segment HK relative to the horizontal plane
    theta = angle_GHM + angle_arm - angle_GHK

    # Calculating position of the boom/arm piston rod attachment in the arm frame
    x_G = -HG * np.sin(alpha)
    z_G = HG * np.cos(alpha)

    # Calculating position of the arm/bucket piston cylinder attachment in the arm frame
    x_I = HI * np.cos(beta)
    z_I = HI * np.sin(beta)

    # Calculating position of the H link attachment in the arm frame
    x_K = HK * np.cos(theta)
    z_K = HK * np.sin(theta)

    # Calculating position of the bucket attachment in the arm frame
    x_M = HM * np.cos(angle_arm)
    z_M = HM * np.sin(angle_arm)

    # Calculating total length of the boom/arm piston
    FG = np.sqrt((x_G - x_F)**2 + (z_G - z_F)**2)

    # Calculating angle of the boom/arm piston relative to the horizontal plane
    angle_ba_piston = np.arcsin((z_G - z_F) / FG)

    return [x_I, z_I, x_K, z_K, x_M, z_M, FG - piston_cylinder_length, angle_ba_piston]


def _calc_H_link_pose(
        angle_bucket: float, x_I: float, z_I: float, x_K: float, z_K: float, x_M: float,
        z_M: float) -> list:
    """Calculates the H link and bucket pose.

    This function calculates all the properties required to set the H link in the
    MuJoCo model.

    Some information about this function:
    - All distances are given in cm.
    - All angles are given in radian.
    - The position of L is given in the bucket frame.
    - The position of J is given in the arm frame.

    The reasoning behind the calculation as well as the convention used are available in
    the model readme.

    Args:
        angle_bucket: Angle of the bucket relative to the horizontal plane. [rad]
        x_I: Position of the arm/bucket piston cylinder attachment in the X direction
             given in the arm frame. [cm]
        z_I: Position of the arm/bucket piston cylinder attachment in the Z direction
             given in the arm frame. [cm]
        x_K: Position of the H link attachment in the X direction given in the arm
             frame. [cm]
        z_K: Position of the H link attachment in the Z direction given in the arm
             frame. [cm]
        x_M: Position of the bucket attachment in the X direction given in the arm
             frame. [cm]
        z_M: Position of the bucket attachment in the Z direction given in the arm
             frame. [cm]

    Returns:
        A list containing the position of the piston rod in the arm/bucket piston
        cylinder, the angle of the H link relative to the IJ segment, the angle of the
        arm/bucket piston relative to the HM segment, the position of the side link
        attachment in the bucket frame (X and Z direction), and the angle of the side
        link relative to the LM segment.
    """
    # Input parameters measured from meshes
    JK = 45.4
    JL = 44.9
    LM = 37.9
    piston_cylinder_length = 86.6

    # Calculating position of the side link attachment in the bucket frame
    x_L = LM * np.cos(angle_bucket)
    z_L = LM * np.sin(angle_bucket)

    # Calculating the KL distance
    KL = np.sqrt((x_L + x_M - x_K)**2 + (z_L + z_M - z_K)**2)

    # Calculating the angle at the H link attachment formed by
    # the side link/H link triangle
    angle_JKL = np.arccos((JK * JK + KL * KL - JL * JL) / (2 * JK * KL))

    # Calculating the angle at the arm/bucket piston rod attachment formed by
    # the side link/H link triangle
    angle_LJK = np.arccos((JK * JK + JL * JL - KL * KL) / (2 * JK * JL))

    # Calculating angle of the segment KL relative to the horizontal plane
    alpha = np.arcsin((z_L + z_M - z_K) / KL)

    # Calculating position of the arm/bucket piston rod attachment in the arm frame
    x_J = x_K + JK * np.cos(angle_JKL + alpha)
    z_J = z_K + JK * np.sin(angle_JKL + alpha)

    # Calculating total length of the arm/bucket piston
    IJ = np.sqrt((x_I - x_J)**2 + (z_I - z_J)**2)

    # Calculating the angle of the arm/H link relative to the HM segment
    angle_ah_piston = np.arcsin((z_J - z_I) / IJ)

    # Calculating the angle of the side link relative to the horizontal plane
    angle_side_link = np.arccos((x_J - x_M - x_L) / JL)

    # Calculating the angle of the H link relative to the IJ segment
    angle_h_link = angle_LJK + np.pi - angle_side_link + angle_ah_piston

    return [
        IJ - piston_cylinder_length, angle_h_link, angle_ah_piston, x_L, z_L,
        -angle_side_link
    ]


if __name__ == "__main__":
    _calc_excavator_pose(np.deg2rad(30), np.deg2rad(-30.), np.deg2rad(40.))
