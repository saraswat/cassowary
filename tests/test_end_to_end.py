import random
from unittest import TestCase

from cassowary.constraint import Equation, Inequality, StayConstraint
from cassowary.error import RequiredFailure
from cassowary.expression import Expression
from cassowary.simplex_solver import SimplexSolver
from cassowary.strength import STRONG, WEAK, MEDIUM, REQUIRED
from cassowary.utils import approx_equal
from cassowary.variable import Variable


class EndToEndTestCase(TestCase):
    def test_simple(self):
        solver = SimplexSolver()

        x = Variable('x', 167)
        y = Variable('y', 2)
        eq = Equation(x, Expression(y))

        solver.add_constraint(eq)
        self.assertAlmostEqual(x.value, y.value)
        self.assertAlmostEqual(x.value, 0)
        self.assertAlmostEqual(y.value, 0)

    def test_stay(self):
        x = Variable('x', 5)
        y = Variable('y', 10)

        solver = SimplexSolver()
        solver.add_stay(x)
        solver.add_stay(y)

        self.assertAlmostEqual(x.value, 5)
        self.assertAlmostEqual(y.value, 10)

    def test_variable_geq_constant(self):
        solver = SimplexSolver()

        x = Variable('x', 10)
        ieq = Inequality(x, Inequality.GEQ, 100)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 100)

    def test_variable_leq_constant(self):
        solver = SimplexSolver()

        x = Variable('x', 100)
        ieq = Inequality(x, Inequality.LEQ, 10)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 10)

    def test_variable_equal_constant(self):
        solver = SimplexSolver()

        x = Variable('x', 10)
        eq = Equation(100, x)
        solver.add_constraint(eq)

        self.assertAlmostEqual(x.value, 100)

    def test_constant_geq_variable(self):
        # 10 >= x
        solver = SimplexSolver()

        x = Variable('x', 100)
        ieq = Inequality(10, Inequality.GEQ, x)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 10)

    def test_constant_leq_variable(self):
        # 100 <= x
        solver = SimplexSolver()

        x = Variable('x', 10)
        ieq = Inequality(100, Inequality.LEQ, x)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 100)

    def test_geq_with_stay(self):
        # stay width
        # right >= 100
        solver = SimplexSolver()

        # x = 10
        x = Variable('x', 10)
        # width = 10
        width = Variable('width', 10)
        # right = x + width
        right = Expression(x) + width
        # right >= 100
        ieq = Inequality(right, Inequality.GEQ, 100)
        solver.add_stay(width)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 90)
        self.assertAlmostEqual(width.value, 10)

    def test_leq_with_stay(self):
        # stay width
        # 100 <= right
        solver = SimplexSolver()

        x = Variable('x', 10)
        width = Variable('width', 10)
        right = Expression(x) + width
        ieq = Inequality(100, Inequality.LEQ, right)

        solver.add_stay(width)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 90)
        self.assertAlmostEqual(width.value, 10)

    def test_equality_with_stay(self):
        # stay width, rightMin
        # right >= rightMin
        solver = SimplexSolver()

        x = Variable('x', 10)
        width = Variable('width', 10)
        rightMin = Variable('rightMin', 100)

        right = Expression(x) + width

        eq = Equation(right, rightMin)

        solver.add_stay(width)
        solver.add_stay(rightMin)
        solver.add_constraint(eq)

        self.assertAlmostEqual(x.value, 90)
        self.assertAlmostEqual(width.value, 10)

    def test_geq_with_variable(self):
        # stay width, rightMin
        # right >= rightMin
        solver = SimplexSolver()

        x = Variable('x', 10)
        width = Variable('width', 10)
        rightMin = Variable('rightMin', 100)

        right = Expression(x) + width

        ieq = Inequality(right, Inequality.GEQ, rightMin)

        solver.add_stay(width)
        solver.add_stay(rightMin)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 90)
        self.assertAlmostEqual(width.value, 10)

    def test_leq_with_variable(self):
        # stay width
        # right >= rightMin
        solver = SimplexSolver()

        x = Variable('x', 10)
        width = Variable('width', 10)
        rightMin = Variable('rightMin', 100)

        right = Expression(x) + width

        ieq = Inequality(rightMin, Inequality.LEQ, right)

        solver.add_stay(width)
        solver.add_stay(rightMin)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x.value, 90)
        self.assertAlmostEqual(width.value, 10)

    def test_equality_with_expression(self):
        # stay width, rightMin
        # right >= rightMin
        solver = SimplexSolver()

        x1 = Variable('x1', 10)
        width1 = Variable('width1', 10)
        right1 = Expression(x1) + width1

        x2 = Variable('x2', 100)
        width2 = Variable('width2', 10)
        right2 = Expression(x2) + width2

        eq = Equation(right1, right2)

        solver.add_stay(width1)
        solver.add_stay(width2)
        solver.add_stay(x2)
        solver.add_constraint(eq)

        self.assertAlmostEqual(x1.value, 100)
        self.assertAlmostEqual(x2.value, 100)
        self.assertAlmostEqual(width1.value, 10)
        self.assertAlmostEqual(width2.value, 10)

    def test_geq_with_expression(self):
        # stay width, rightMin
        # right >= rightMin
        solver = SimplexSolver()

        x1 = Variable('x1', 10)
        width1 = Variable('width1', 10)
        right1 = Expression(x1) + width1

        x2 = Variable('x2', 100)
        width2 = Variable('width2', 10)
        right2 = Expression(x2) + width2

        ieq = Inequality(right1, Inequality.GEQ, right2)

        solver.add_stay(width1)
        solver.add_stay(width2)
        solver.add_stay(x2)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x1.value, 100)

    def test_leq_with_expression(self):
        # stay width, rightMin
        # right >= rightMin
        solver = SimplexSolver()

        x1 = Variable('x1', 10)
        width1 = Variable('width1', 10)
        right1 = Expression(x1) + width1

        x2 = Variable('x2', 100)
        width2 = Variable('width2', 10)
        right2 = Expression(x2) + width2

        ieq = Inequality(right2, Inequality.LEQ, right1)

        solver.add_stay(width1)
        solver.add_stay(width2)
        solver.add_stay(x2)
        solver.add_constraint(ieq)

        self.assertAlmostEqual(x1.value, 100)

    def test_delete1(self):
        solver = SimplexSolver()
        x = Variable('x')
        cbl = Equation(x, 100, WEAK)
        solver.add_constraint(cbl)

        c10 = Inequality(x, Inequality.LEQ, 10)
        c20 = Inequality(x, Inequality.LEQ, 20)
        solver.add_constraint(c10)
        solver.add_constraint(c20)
        self.assertAlmostEqual(x.value, 10)

        solver.remove_constraint(c10)
        self.assertAlmostEqual(x.value, 20)

        solver.remove_constraint(c20)
        self.assertAlmostEqual(x.value, 100)

        c10again = Inequality(x, Inequality.LEQ, 10)
        solver.add_constraint(c10)
        solver.add_constraint(c10again)
        self.assertAlmostEqual(x.value, 10)

        solver.remove_constraint(c10)
        self.assertAlmostEqual(x.value, 10)

        solver.remove_constraint(c10again)
        self.assertAlmostEqual(x.value, 100)

    def test_delete2(self):
        solver = SimplexSolver()
        x = Variable('x')
        y = Variable('y')

        solver.add_constraint(Equation(x, 100, WEAK))
        solver.add_constraint(Equation(y, 120, STRONG))
        c10 = Inequality(x, Inequality.LEQ, 10)
        c20 = Inequality(x, Inequality.LEQ, 20)
        solver.add_constraint(c10)
        solver.add_constraint(c20)
        self.assertAlmostEqual(x.value, 10)
        self.assertAlmostEqual(y.value, 120)

        solver.remove_constraint(c10)
        self.assertAlmostEqual(x.value, 20)
        self.assertAlmostEqual(y.value, 120)

        cxy = Equation(x * 2, y)
        solver.add_constraint(cxy)
        self.assertAlmostEqual(x.value, 20)
        self.assertAlmostEqual(y.value, 40)

        solver.remove_constraint(c20)
        self.assertAlmostEqual(x.value, 60)
        self.assertAlmostEqual(y.value, 120)

        solver.remove_constraint(cxy)
        self.assertAlmostEqual(x.value, 100)
        self.assertAlmostEqual(y.value, 120)

    def test_casso1(self):
        solver = SimplexSolver()
        x = Variable('x')
        y = Variable('y')

        solver.add_constraint(Inequality(x, Inequality.LEQ, y))
        solver.add_constraint(Equation(y, x + 3))
        solver.add_constraint(Equation(x, 10, WEAK))
        solver.add_constraint(Equation(y, 10, WEAK))

        self.assertTrue(
            (approx_equal(x.value, 10) and approx_equal(y.value, 13)) or
            (approx_equal(x.value,  7) and approx_equal(y.value, 10))
        )

    def test_inconsistent1(self):
        solver = SimplexSolver()
        x = Variable('x')
        # x = 10
        solver.add_constraint(Equation(x, 10))
        # x = 5
        with self.assertRaises(RequiredFailure):
            solver.add_constraint(Equation(x, 5))

    def test_inconsistent2(self):
        solver = SimplexSolver()
        x = Variable('x')
        solver.add_constraint(Inequality(x, Inequality.GEQ, 10))

        with self.assertRaises(RequiredFailure):
            solver.add_constraint(Inequality(x, Inequality.LEQ, 5))

    def test_inconsistent3(self):
        solver = SimplexSolver()
        w = Variable('w')
        x = Variable('x')
        y = Variable('y')
        z = Variable('z')
        solver.add_constraint(Inequality(w, Inequality.GEQ, 10))
        solver.add_constraint(Inequality(x, Inequality.GEQ, w))
        solver.add_constraint(Inequality(y, Inequality.GEQ, x))
        solver.add_constraint(Inequality(z, Inequality.GEQ, y))
        solver.add_constraint(Inequality(z, Inequality.GEQ, 8))

        with self.assertRaises(RequiredFailure):
            solver.add_constraint(Inequality(z, Inequality.LEQ, 4))

    def test_inconsistent4(self):
        solver = SimplexSolver()
        x = Variable('x')
        y = Variable('y')
        # x = 10
        solver.add_constraint(Equation(x, 10))
        # x = y
        solver.add_constraint(Equation(x, y))
        # y = 5. Should fail.
        with self.assertRaises(RequiredFailure):
            solver.add_constraint(Equation(y, 5))

    def test_multiedit1(self):
        # This test stresses the edit session stack. begin_edit() starts a new
        # "edit variable group" and "end_edit" closes it, leaving only the
        # previously opened edit variables still active.
        x = Variable('x')
        y = Variable('y')
        w = Variable('w')
        h = Variable('h')
        solver = SimplexSolver()
        # Add some stays and start an editing session
        solver.add_stay(x)
        solver.add_stay(y)
        solver.add_stay(w)
        solver.add_stay(h)
        solver.add_edit_var(x)
        solver.add_edit_var(y)
        solver.begin_edit()

        solver.suggest_value(x, 10)
        solver.suggest_value(y, 20)
        solver.resolve()

        self.assertAlmostEqual(x.value, 10)
        self.assertAlmostEqual(y.value, 20)
        self.assertAlmostEqual(w.value, 0)
        self.assertAlmostEqual(h.value, 0)

        # Open a second set of variables for editing
        solver.add_edit_var(w)
        solver.add_edit_var(h)
        solver.begin_edit()
        solver.suggest_value(w, 30)
        solver.suggest_value(h, 40)
        solver.end_edit()

        # Close the second set...
        self.assertAlmostEqual(x.value, 10)
        self.assertAlmostEqual(y.value, 20)
        self.assertAlmostEqual(w.value, 30)
        self.assertAlmostEqual(h.value, 40)

        # Now make sure the first set can still be edited
        solver.suggest_value(x, 50)
        solver.suggest_value(y, 60)
        solver.end_edit()
        self.assertAlmostEqual(x.value, 50)
        self.assertAlmostEqual(y.value, 60)
        self.assertAlmostEqual(w.value, 30)
        self.assertAlmostEqual(h.value, 40)

    def test_multiedit2(self):

        x = Variable('x')
        y = Variable('y')
        w = Variable('w')
        h = Variable('h')

        solver = SimplexSolver()
        solver.add_stay(x)
        solver.add_stay(y)
        solver.add_stay(w)
        solver.add_stay(h)
        solver.add_edit_var(x)
        solver.add_edit_var(y)

        solver.begin_edit()
        solver.suggest_value(x, 10)
        solver.suggest_value(y, 20)
        solver.resolve()
        solver.end_edit()

        self.assertAlmostEqual(x.value, 10)
        self.assertAlmostEqual(y.value, 20)
        self.assertAlmostEqual(w.value, 0)
        self.assertAlmostEqual(h.value, 0)

        solver.add_edit_var(w)
        solver.add_edit_var(h)

        solver.begin_edit()
        solver.suggest_value(w, 30)
        solver.suggest_value(h, 40)
        solver.end_edit()

        self.assertAlmostEqual(x.value, 10)
        self.assertAlmostEqual(y.value, 20)
        self.assertAlmostEqual(w.value, 30)
        self.assertAlmostEqual(h.value, 40)

        solver.add_edit_var(x)
        solver.add_edit_var(y)

        solver.begin_edit()
        solver.suggest_value(x, 50)
        solver.suggest_value(y, 60)
        solver.end_edit()

        self.assertAlmostEqual(x.value, 50)
        self.assertAlmostEqual(y.value, 60)
        self.assertAlmostEqual(w.value, 30)
        self.assertAlmostEqual(h.value, 40)

    def test_multiedit3(self):
        MIN = 100
        MAX = 500

        width = Variable('width')
        height = Variable('height')
        top = Variable('top')
        bottom = Variable('bottom')
        left = Variable('left')
        right = Variable('right')

        solver = SimplexSolver()

        iw = Variable('window_innerWidth', random.randrange(MIN, MAX))
        ih = Variable('window_innerHeight', random.randrange(MIN, MAX))

        solver.add_constraint(Equation(width, iw, strength=STRONG, weight=0.0))
        solver.add_constraint(Equation(height, ih, strength=STRONG, weight=0.0))
        solver.add_constraint(Equation(top, 0, strength=WEAK, weight=0.0))
        solver.add_constraint(Equation(left, 0, strength=WEAK, weight=0.0))
        solver.add_constraint(Equation(bottom, top + height, strength=MEDIUM, weight=0.0))
        # Right is at least left + width
        solver.add_constraint(Equation(right,  left + width, strength=MEDIUM, weight=0.0))
        solver.add_constraint(StayConstraint(iw))
        solver.add_constraint(StayConstraint(ih))

        # Propegate viewport size changes.
        for i in range(0, 30):

            # Measurement should be cheap here.
            iwv = random.randrange(MIN, MAX)
            ihv = random.randrange(MIN, MAX)

            solver.add_edit_var(iw)
            solver.add_edit_var(ih)

            solver.begin_edit()
            solver.suggest_value(iw, iwv)
            solver.suggest_value(ih, ihv)
            solver.resolve()
            solver.end_edit()

            self.assertAlmostEqual(top.value, 0)
            self.assertAlmostEqual(left.value, 0)
            self.assertLessEqual(bottom.value, MAX)
            self.assertGreaterEqual(bottom.value, MIN)
            self.assertLessEqual(right.value, MAX)
            self.assertGreaterEqual(right.value, MIN)

    def test_error_weights(self):
        solver = SimplexSolver()

        x = Variable('x', 100)
        y = Variable('y', 200)
        z = Variable('z', 50)

        self.assertAlmostEqual(x.value, 100)
        self.assertAlmostEqual(y.value, 200)
        self.assertAlmostEqual(z.value, 50)

        solver.add_constraint(Equation(z, x, WEAK))
        solver.add_constraint(Equation(x, 20, WEAK))
        solver.add_constraint(Equation(y, 200, STRONG))

        self.assertAlmostEqual(x.value,  20)
        self.assertAlmostEqual(y.value, 200)
        self.assertAlmostEqual(z.value,  20)

        solver.add_constraint(Inequality(z + 150, Inequality.LEQ, y, MEDIUM))

        self.assertAlmostEqual(x.value, 20)
        self.assertAlmostEqual(y.value, 200)
        self.assertAlmostEqual(z.value, 20)

    def test_quadrilateral(self):
        "A simple version of the quadrilateral test"

        solver = SimplexSolver()

        class Point(object):
            def __init__(self, x, y, identifier):
                self.x = Variable('x' + identifier, x)
                self.y = Variable('y' + identifier, y)

            def __repr__(self):
                return u'(%s, %s)' % (self.x.value, self.y.value)

            def __eq__(self, other):
                return self.x.value == other[0] and self.y.value == other[1]

        points = [
            Point(10, 10, '0'),
            Point(10, 200, '1'),
            Point(200, 200, '2'),
            Point(200, 10, '3'),

            Point(0, 0, 'm0'),
            Point(0, 0, 'm1'),
            Point(0, 0, 'm2'),
            Point(0, 0, 'm3'),
        ]
        midpoints = points[4:]

        # Add point stays
        weight = 1.0
        multiplier = 2.0
        for i, point in enumerate(points[:4]):
            solver.add_stay(point.x, WEAK, weight)
            solver.add_stay(point.y, WEAK, weight)
            weight = weight * multiplier

        for start, end in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            cle = (Expression(variable=points[start].x) + points[end].x) / 2
            cleq = Equation(midpoints[start].x, cle)
            solver.add_constraint(cleq)
            cle = (Expression(variable=points[start].y) + points[end].y) / 2
            cleq = Equation(midpoints[start].y, cle)
            solver.add_constraint(cleq)

        cle = Expression(variable=points[0].x) + Expression(constant=20)
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[2].x))
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[3].x))

        cle = Expression(variable=points[1].x) + Expression(constant=20)
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[2].x))
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[3].x))

        cle = Expression(variable=points[0].y) + Expression(constant=20)
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[1].y))
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[2].y))

        cle = Expression(variable=points[3].y) + Expression(constant=20)
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[1].y))
        solver.add_constraint(Inequality(cle, Inequality.LEQ, points[2].y))

        for point in points:
            solver.add_constraint(Inequality(point.x, Inequality.GEQ, 10))

            solver.add_constraint(Inequality(point.y, Inequality.GEQ, 10))

            solver.add_constraint(Inequality(point.x, Inequality.LEQ, 500))
            solver.add_constraint(Inequality(point.y, Inequality.LEQ, 500))

        # Now move point 2 to a new location

        solver.add_edit_var(points[2].x)
        solver.add_edit_var(points[2].y)

        solver.begin_edit()

        solver.suggest_value(points[2].x, 300)
        solver.suggest_value(points[2].y, 400)

        solver.end_edit()

        # Check that the other points have been moved.
        self.assertEqual(points[0], (10.0, 10.0))
        self.assertEqual(points[1], (10.0, 200.0))
        self.assertEqual(points[2], (300.0, 400.0))
        self.assertEqual(points[3], (200.0, 10.0))
        self.assertEqual(points[4], (10.0, 105.0))
        self.assertEqual(points[5], (155.0, 300.0))
        self.assertEqual(points[6], (250.0, 205.0))
        self.assertEqual(points[7], (105.0, 10.0))

    def test_buttons(self):
        "A test of a horizontal layout of two buttons on a screen."

        class Button(object):
            def __init__(self, identifier):
                self.left = Variable('left' + identifier, 0)
                self.width = Variable('width' + identifier, 0)

            def __repr__(self):
                return u'(%s:%s)' % (self.left.value, self.width.value)

        solver = SimplexSolver()

        b1 = Button('b1')
        b2 = Button('b2')
        left_limit = Variable('left', 0)
        right_limit = Variable('width', 0)

        left_limit.value = 0
        solver.add_constraint(StayConstraint(left_limit, REQUIRED))
        stay = StayConstraint(right_limit, WEAK)
        solver.add_constraint(stay)

        # The two buttons are the same width
        solver.add_constraint(
            Equation(
                Expression(variable=b1.width),
                Expression(variable=b2.width),
            )
        )

        # b1 starts 50 from the left margin.
        solver.add_constraint(
            Equation(
                Expression(variable=b1.left),
                Expression(variable=left_limit) + 50
            )
        )

        # b2 ends 50 from the right margin
        solver.add_constraint(
            Equation(
                Expression(variable=left_limit) + Expression(variable=right_limit),
                Expression(variable=b2.left) + Expression(variable=b2.width) + 50,
            ),
        )

        # b2 starts at least 100 from the end of b1
        solver.add_constraint(
            Inequality(
                Expression(variable=b2.left),
                Inequality.GEQ,
                Expression(variable=b1.left) + Expression(variable=b1.width) + 100,
            )
        )

        # b1 has a minimum width of 87
        solver.add_constraint(
            Inequality(
                Expression(variable=b1.width),
                Inequality.GEQ,
                87,
            )
        )

        # b1's preferred width is 87
        solver.add_constraint(
            Equation(
                Expression(variable=b1.width),
                87,
                strength=STRONG
            )
        )

        # b2's minimum width is 113
        solver.add_constraint(
            Inequality(
                Expression(variable=b2.width),
                Inequality.GEQ,
                113,
            )
        )

        # b2's preferred width is 113
        solver.add_constraint(
            Equation(
                Expression(variable=b2.width),
                113,
                strength=STRONG
            )
        )

        # Without imposign a stay on the right, right_limit will be the minimum width for the layout
        self.assertAlmostEqual(b1.left.value, 50.0)
        self.assertAlmostEqual(b1.width.value, 113.0)
        self.assertAlmostEqual(b2.left.value, 263.0)
        self.assertAlmostEqual(b2.width.value, 113.0)
        self.assertAlmostEqual(right_limit.value, 426.0)
        solver.remove_constraint(stay)

        # The window is 500 pixels wide.
        right_limit.value = 500
        stay = StayConstraint(right_limit, REQUIRED)
        solver.add_constraint(stay)
        self.assertAlmostEqual(b1.left.value, 50.0)
        self.assertAlmostEqual(b1.width.value, 113.0)
        self.assertAlmostEqual(b2.left.value, 337.0)
        self.assertAlmostEqual(b2.width.value, 113.0)
        self.assertAlmostEqual(right_limit.value, 500.0)
        solver.remove_constraint(stay)

        # Expand to 700 pixels
        right_limit.value = 700
        stay = StayConstraint(right_limit, REQUIRED)
        solver.add_constraint(stay)
        self.assertAlmostEqual(b1.left.value, 50.0)
        self.assertAlmostEqual(b1.width.value, 113.0)
        self.assertAlmostEqual(b2.left.value, 537.0)
        self.assertAlmostEqual(b2.width.value, 113.0)
        self.assertAlmostEqual(right_limit.value, 700.0)
        solver.remove_constraint(stay)

        # Contract to 600
        right_limit.value = 600
        stay = StayConstraint(right_limit, REQUIRED)
        solver.add_constraint(stay)
        self.assertAlmostEqual(b1.left.value, 50.0)
        self.assertAlmostEqual(b1.width.value, 113.0)
        self.assertAlmostEqual(b2.left.value, 437.0)
        self.assertAlmostEqual(b2.width.value, 113.0)
        self.assertAlmostEqual(right_limit.value, 600.0)
        solver.remove_constraint(stay)