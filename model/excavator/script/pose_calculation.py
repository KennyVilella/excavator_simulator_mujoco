"""Calculates pose of an excavator.

The purpose of the functions in this file is to calculate the pose of the different
parts of an excavator provided the boom, arm and bucket angle.
The math behind the calculation is provided in the model readme.

Copyright, 2023,  Vilella Kenny.
"""
import numpy as np
#======================================================================================#
#                                                                                      #
#       Starting implementation of functions used to calculate the excavator pose      #
#                                                                                      #
#======================================================================================#
def _calc_excavator_pose(
    angle_boom: float, angle_arm: float, angle_bucket: float) -> list:
    """
    """
    # Calculating the pose of the boom
    x_E, z_E, x_F, z_F, x_H, z_H, ED, angle_chassis_boom_piston = _calc_boom_pose(
        angle_boom)
    # Printing outputs
    print("\n================= Boom pose =================")
    print("E: (%.2f, %.2f)\nH: (%.2f, %.2f)" % (x_E, z_E, x_H, z_H))
    print("F: (%.2f, %.2f)\nED: %.2f\next: %.2f" % (x_F, z_F, ED, ED-133.6))

    print("angle_chassis_boom_piston: %.2f rad, %.2f deg" %
        (angle_chassis_boom_piston, np.rad2deg(angle_chassis_boom_piston)))

    # Calculating the pose of the arm
    x_G, z_G, x_I, z_I, x_K, z_K, x_M, z_M, FG, angle_boom_arm_piston = _calc_arm_pose(
        angle_arm, x_F - x_H, z_F - z_H)
    # Printing outputs
    print("\n================= Arm pose =================")
    print("G: (%.2f, %.2f)\nI: (%.2f, %.2f)" % (x_G, z_G, x_I, z_I))
    print("K: (%.2f, %.2f)\nM: (%.2f, %.2f)" % (x_K, z_K, x_M, z_M))
    print("FG: %.2f\next: %.2f" % (FG, FG-114.7))
    print("angle_boom_arm_piston: %.2f rad, %.2f deg" %
        (angle_boom_arm_piston, np.rad2deg(angle_boom_arm_piston)))

    # Calculating the pose of the H link and bucket
    x_J, z_J, x_L, z_L, IJ, angle_h_link, angle_arm_h_link_piston, angle_side_link = (
        _calc_H_link_pose(angle_bucket, x_I, z_I, x_K, z_K, x_M, z_M))
    # Printing outputs
    print("\n================= H link pose =================")
    print("J: (%.2f, %.2f)\nIJ: %.2f\next: %.2f" % (x_J, z_J, IJ, IJ-86.56))
    print("angle_arm_h_link_piston: %.2f rad, %.2f deg" %
        (angle_arm_h_link_piston, np.rad2deg(angle_arm_h_link_piston)))
    print("angle_h_link: %.2f rad, %.2f deg" % (angle_h_link, np.rad2deg(angle_h_link)))
    print("angle_side_link: %.2f rad, %.2f deg" %
        (angle_side_link, np.rad2deg(angle_side_link)))
    print("\n================= Bucket pose =================")
    print("L: (%.2f, %.2f)" % (x_L, z_L))

def _calc_boom_pose(angle_boom: float) -> list:
    """
    """
    # Input parameters
    CH = 384.5
    #EH = 241.3
    CE = 167.8
    CF = 236.2
    FH = 192.7
    x_D = 47.4
    z_D = -23.7
    angle_HCE = 0.421
    angle_HCF = 0.411

    # Calculating outputs
    x_E = CE * np.cos(angle_boom + angle_HCE)
    z_E = CE * np.sin(angle_boom + angle_HCE)
    x_H = CH * np.cos(angle_boom)
    z_H = CH * np.sin(angle_boom)
    x_F = CF * np.cos(angle_boom + angle_HCF)
    z_F = CF * np.sin(angle_boom + angle_HCF)
    ED = np.sqrt((x_E - x_D) ** 2 + (z_E - z_D) ** 2)
    angle_chassis_boom_piston = np.arccos((x_E - x_D) / ED)

    return [x_E, z_E, x_F, z_F, x_H, z_H, ED, angle_chassis_boom_piston]

def _calc_arm_pose(angle_arm: float, x_F: float, z_F: float) -> list:
    """
    """
    # Input parameters
    HG = 57.0
    HM = 199.6
    HI = 44.8
    HK = 152.3
    #KG = 207.4
    #KM = 47.8
    #GM = 255.1
    #GI = 82.4
    angle_GHM = 2.881
    angle_GHI = 1.876
    angle_GHK = 2.838
    alpha = angle_GHM - angle_arm - np.pi / 2
    beta = angle_GHM - angle_arm - angle_GHI
    theta = angle_GHM - angle_arm - angle_GHK

    # Calculating outputs
    x_G = -HG * np.sin(alpha)
    z_G = HG * np.cos(alpha)
    x_I = HI * np.cos(beta)
    z_I = HI * np.sin(beta)
    x_K = HK * np.cos(theta)
    z_K = HK * np.sin(theta)
    x_M = HM * np.cos(angle_arm)
    z_M = -HM * np.sin(angle_arm)
    FG = np.sqrt((x_G - x_F) ** 2 + (z_G - z_F) ** 2)
    angle_boom_arm_piston = np.arccos((x_G - x_F) / FG)

    return [x_G, z_G, x_I, z_I, x_K, z_K, x_M, z_M, FG, angle_boom_arm_piston]

def _calc_H_link_pose(
    angle_bucket: float, x_I: float, z_I: float, x_K: float, z_K: float,
    x_M: float, z_M: float) -> list:
    """
    """
    # Input parameters
    JK = 45.4
    JL = 44.9
    LM = 37.9

    # Calculating outputs
    x_L = LM * np.cos(angle_bucket)
    z_L = LM * np.sin(angle_bucket)
    KL = np.sqrt((x_L + x_M - x_K) ** 2 + (z_L + z_M - z_K) ** 2)
    angle_JKL = np.arccos((JK * JK + KL * KL - JL * JL) / (2 * JK * KL))
    alpha = np.arcsin((z_L + z_M - z_K) / KL)
    angle_h_link = angle_JKL + alpha
    x_J = x_K + JK * np.cos(angle_h_link)
    z_J = z_K + JK * np.sin(angle_h_link)
    IJ = np.sqrt((x_I - x_J) ** 2 + (z_I - z_J) ** 2)
    angle_arm_h_link_piston = np.arccos((x_J - x_I) / IJ)
    angle_side_link = np.arccos((x_L + x_M - x_J) / JL)

    return [x_J, z_J, x_L, z_L, IJ, angle_h_link, angle_arm_h_link_piston, angle_side_link]

if __name__ == "__main__":
    _calc_excavator_pose(np.deg2rad(.0), np.deg2rad(0.), np.deg2rad(00))
