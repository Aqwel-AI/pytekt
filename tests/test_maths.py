import aion


def test_basic_arithmetic():
    assert aion.maths.addition(2, 3) == 5
    assert aion.maths.subtraction(5, 2) == 3
    assert aion.maths.multiplication(2, 3) == 6
    assert aion.maths.division(6, 3) == 2
