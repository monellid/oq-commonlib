import unittest
from openquake.hazardlib import imt
from openquake.commonlib import valid


class ValidationTestCase(unittest.TestCase):
    # more is done in the doctests inside commonlib.valid

    def test_name(self):
        self.assertEqual(valid.name('x'), 'x')
        with self.assertRaises(ValueError):
            valid.name('1')
        with self.assertRaises(ValueError):
            valid.name('x y')

    def test_namelist(self):
        self.assertEqual(valid.namelist('x y'), ['x', 'y'])
        with self.assertRaises(ValueError):
            valid.namelist('')
        with self.assertRaises(ValueError):
            valid.namelist('x 1')

    def test_longitude(self):
        self.assertEqual(valid.longitude('1'), 1.0)
        self.assertEqual(valid.longitude('180'), 180.0)
        with self.assertRaises(ValueError):
            valid.longitude('181')
        with self.assertRaises(ValueError):
            valid.longitude('-181')

    def test_latitude(self):
        self.assertEqual(valid.latitude('1'), 1.0)
        self.assertEqual(valid.latitude('90'), 90.0)
        with self.assertRaises(ValueError):
            valid.latitude('91')
        with self.assertRaises(ValueError):
            valid.latitude('-91')

    def test_positiveint(self):
        self.assertEqual(valid.positiveint('1'), 1)
        with self.assertRaises(ValueError):
            valid.positiveint('-1')
        with self.assertRaises(ValueError):
            valid.positiveint('1.1')
        with self.assertRaises(ValueError):
            valid.positiveint('1.0')

    def test_positivefloat(self):
        self.assertEqual(valid.positiveint('1'), 1)
        with self.assertRaises(ValueError):
            valid.positivefloat('-1')
        self.assertEqual(valid.positivefloat('1.1'), 1.1)

    def test_probability(self):
        self.assertEqual(valid.probability('1'), 1.0)
        self.assertEqual(valid.probability('.5'), 0.5)
        self.assertEqual(valid.probability('0'), 0.0)
        with self.assertRaises(ValueError):
            valid.probability('1.1')
        with self.assertRaises(ValueError):
            valid.probability('-0.1')

    def test_IMTstr(self):
        self.assertEqual(imt.from_string('SA(1)'), ('SA', 1, 5))
        self.assertEqual(imt.from_string('SA(1.)'), ('SA', 1, 5))
        self.assertEqual(imt.from_string('SA(0.5)'), ('SA', 0.5, 5))
        self.assertEqual(imt.from_string('PGV'), ('PGV', None, None))
        with self.assertRaises(ValueError):
            imt.from_string('S(1)')

    def test_choice(self):
        validator = valid.Choice('aggregated', 'per_asset')
        self.assertEqual(validator('aggregated'), 'aggregated')
        self.assertEqual(validator('per_asset'), 'per_asset')
        with self.assertRaises(ValueError):
            validator('xxx')

    def test_empty(self):
        self.assertEqual(valid.not_empty("text"), "text")
        with self.assertRaises(ValueError):
            valid.not_empty("")

    def test_none_or(self):
        validator = valid.NoneOr(valid.positiveint)
        self.assertEqual(validator(''), None)
        self.assertEqual(validator('1'), 1)
