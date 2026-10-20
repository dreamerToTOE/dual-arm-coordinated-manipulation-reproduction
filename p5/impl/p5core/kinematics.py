"""Planar chain kinematics and the feature maps used by the SCA tasks.

There is no claim that this geometry is the IIWA of the paper.  It is a
low-dimensional, fully analytic arm whose Jacobians can be checked in closed
form, which is exactly what the review asked for in T07/T08: verify the
*derivative chain*, not a guessed robot model.

Everything planar here is labelled ENGINEERING (structure) or ADAPTATION
(geometry), never ORIGINAL.
"""

import numpy as np


class PlanarArm:
    """n-link planar chain driven by *relative* joint angles."""

    def __init__(self, lengths, base=(0.0, 0.0)):
        self.l = np.asarray(lengths, dtype=float)
        self.base = np.asarray(base, dtype=float)
        self.n = len(self.l)

    # ------------------------------------------------------------------ FK
    def points(self, q):
        """Joint positions p_0 .. p_n, p_0 = base.

        Relative-angle convention: link i points along the accumulated angle
        ``sum_{j<=i} q_j``.  This is what makes ``d p_n / d q_i = z x (p_n - p_i)``
        hold for every i, i.e. the analytic Jacobian below and the finite
        difference of this FK must agree (test P4.1a pins exactly that).
        """
        q = np.asarray(q, dtype=float).ravel()
        pts = [self.base.copy()]
        acc = self.base.copy()
        ang = 0.0
        for i in range(self.n):
            ang += q[i]
            acc = acc + self.l[i] * np.array([np.cos(ang), np.sin(ang)])
            pts.append(acc.copy())
        return np.array(pts)          # (n+1, 2)

    def eef(self, q):
        return self.points(q)[-1]

    # ------------------------------------------------------------ Jacobians
    def jacobian(self, q, link=None, point=None):
        """d p / d q for one material point of the chain.

        `link` / `point`: if `point` is given (a 2-vector in world frame) the
        Jacobian of that material point is returned, using the joints that
        precede it.  With `link=k` the point is the end of link k.
        """
        q = np.asarray(q, dtype=float).ravel()
        pts = self.points(q)
        if point is None:
            point = pts[-1] if link is None else pts[link + 1]
            upto = self.n if link is None else link + 1
        else:
            upto = self.n
        point = np.asarray(point, dtype=float)
        J = np.zeros((2, self.n))
        for i in range(upto):
            # a joint rotating about z at pts[i]: dp/dq_i = z x (p - p_i)
            d = point - pts[i]
            J[0, i] = -d[1]
            J[1, i] = d[0]
        return J

    def jacobian_fd(self, q, h=1e-6):
        """Central-difference Jacobian of the end effector (for self-checks)."""
        q = np.asarray(q, dtype=float).ravel()
        J = np.zeros((2, self.n))
        for i in range(self.n):
            dq = np.zeros(self.n)
            dq[i] = h
            J[:, i] = (self.eef(q + dq) - self.eef(q - dq)) / (2 * h)
        return J


class DualPlanarArm:
    """Two planar arms in one joint vector q = [q_left, q_right]."""

    def __init__(self, n_per_arm=2, lengths=(0.6, 0.45),
                 base_left=(0.0, 0.0), base_right=(0.0, 1.2)):
        self.left = PlanarArm(lengths, base_left)
        self.right = PlanarArm(lengths, base_right)
        self.n = 2 * n_per_arm
        self.n_arm = n_per_arm

    def split(self, q):
        q = np.asarray(q, dtype=float).ravel()
        return q[:self.n_arm], q[self.n_arm:]

    def eefs(self, q):
        ql, qr = self.split(q)
        return self.left.eef(ql), self.right.eef(qr)

    def jacobians(self, q):
        ql, qr = self.split(q)
        Jl = np.zeros((2, self.n))
        Jr = np.zeros((2, self.n))
        Jl[:, :self.n_arm] = self.left.jacobian(ql)
        Jr[:, self.n_arm:] = self.right.jacobian(qr)
        return Jl, Jr

    def stacked_jacobian(self, q):
        Jl, Jr = self.jacobians(q)
        return np.vstack([Jl, Jr])

    def link_point(self, q, arm, link):
        """World position of the end of `link` on the given arm."""
        ql, qr = self.split(q)
        if arm == 0:
            return self.left.points(ql)[link + 1]
        return self.right.points(qr)[link + 1]

    def link_point_jacobian(self, q, arm, link):
        """(2, n) Jacobian of that material point in the full joint vector."""
        ql, qr = self.split(q)
        J = np.zeros((2, self.n))
        if arm == 0:
            J[:, :self.n_arm] = self.left.jacobian(ql, link=link)
        else:
            J[:, self.n_arm:] = self.right.jacobian(qr, link=link)
        return J
