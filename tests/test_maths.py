import pytekt


def test_basic_arithmetic():
    assert pytekt.maths.addition(2, 3) == 5
    assert pytekt.maths.subtraction(5, 2) == 3
    assert pytekt.maths.multiplication(2, 3) == 6
    assert pytekt.maths.division(6, 3) == 2
