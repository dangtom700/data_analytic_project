import math

# Precomputed constants
R = 2.8614**2 + 126.994**2       # ~ 16135.95
C = 133.3**2 + 0.5**2            # ~ 17769.14

def forward_kinematics(theta1, theta2, theta3):
    """
    Forward kinematics for the given joint angles (in radians).
    Returns the homogeneous transformation matrix ^0_T_ee as a list of lists.
    """
    c1, s1 = math.cos(theta1), math.sin(theta1)
    c2, s2 = math.cos(theta2), math.sin(theta2)
    c23, s23 = math.cos(theta2 + theta3), math.sin(theta2 + theta3)

    # Position terms
    px = c1 * (2.8614 * s23 - 126.994 * c23 - 133.3 * c2 + 0.5 * s2 + 1.3) - 0.2645 * s1
    py = s1 * (2.8614 * s23 - 126.994 * c23 - 133.3 * c2 + 0.5 * s2 + 1.3) + 0.2645 * c1
    pz = 126.994 * s23 + 2.8614 * c23 + 0.5 * c2 + 133.3 * s2 + 95

    # Rotation matrix components
    R00, R01, R02 = c1 * c23, -s1, c1 * s23
    R10, R11, R12 = s1 * c23, c1, s1 * s23
    R20, R21, R22 = -s23, 0, c23

    T = [
        [R00, R01, R02, px],
        [R10, R11, R12, py],
        [R20, R21, R22, pz],
        [0,   0,   0,   1]
    ]
    return T


def inverse_kinematics(x, y, z):
    """
    Inverse kinematics for given end-effector position (x, y, z).
    Returns a list of possible (theta1, theta2, theta3) solutions in radians.
    """
    solutions = []

    # Step 1: theta1
    rho_sq = x**2 + y**2
    if rho_sq < 0.2645**2:
        return []  # No real solution for theta1

    base_angle = math.atan2(x, -y)
    delta_angle = math.acos(-0.2645 / math.sqrt(rho_sq))

    theta1_candidates = [
        base_angle + delta_angle,
        base_angle - delta_angle
    ]

    # Step 2: theta2
    for theta1 in theta1_candidates:
        c1, s1 = math.cos(theta1), math.sin(theta1)
        U = c1 * x + s1 * y - 1.3
        V = z - 95
        M = 133.3 * U - 0.5 * V
        N = -0.5 * U - 133.3 * V
        L = 0.5 * (R - C - U**2 - V**2)

        if M**2 + N**2 < L**2:
            continue  # No real solution for theta2 for this theta1

        base_angle2 = math.atan2(N, M)
        delta_angle2 = math.acos(L / math.sqrt(M**2 + N**2))

        theta2_candidates = [
            base_angle2 + delta_angle2,
            base_angle2 - delta_angle2
        ]

        # Step 3: theta3
        for theta2 in theta2_candidates:
            c2, s2 = math.cos(theta2), math.sin(theta2)
            P = U + 133.3 * c2 - 0.5 * s2
            Q = V - 0.5 * c2 - 133.3 * s2
            s23 = (2.8614 * P + 126.994 * Q) / R
            c23 = (-126.994 * P + 2.8614 * Q) / R

            theta23 = math.atan2(s23, c23)
            theta3 = theta23 - theta2

            solutions.append((theta1, theta2, theta3))

    return solutions


# Example usage:
if __name__ == "__main__":
    # Test FK
    th1, th2, th3 = math.radians(30), math.radians(45), math.radians(-20)
    T = forward_kinematics(th1, th2, th3)
    print("Forward Kinematics Matrix:")
    for row in T:
        print(row)

    # Test IK
    x, y, z = T[0][3], T[1][3], T[2][3]
    print("\nEnd-Effector Position (x, y, z):", (x, y, z))
    ik_solutions = inverse_kinematics(x, y, z)
    print("\nInverse Kinematics Solutions:")
    for sol in ik_solutions:
        print(tuple(math.degrees(a) for a in sol))
