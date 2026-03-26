from __future__ import annotations

import unittest

from zsm_sagemath_lsp.shadow import build_shadow_document, find_word_at_position


class ShadowTests(unittest.TestCase):
    def test_ring_assignment_expands_to_python(self) -> None:
        source = "R.<x, y> = PolynomialRing(ZZ, 'x,y')\n"
        snapshot = build_shadow_document(source)
        self.assertIn("R = PolynomialRing(ZZ, 'x,y')", snapshot.shadow_source)
        self.assertIn("x, y = R.gens()", snapshot.shadow_source)

    def test_function_assignment_becomes_def(self) -> None:
        source = "f(x) = x^2 + 1\n"
        snapshot = build_shadow_document(source)
        self.assertIn("def f(x):", snapshot.shadow_source)
        self.assertIn("return x^2 + 1", snapshot.shadow_source)

    def test_word_detection(self) -> None:
        source = "value = matrix(QQ, [[1]])\n"
        self.assertEqual(find_word_at_position(source, 0, 2), "value")


if __name__ == "__main__":
    unittest.main()
