def assert_patterns_are_equal(pattern_x, pattern_y):
    assert len(pattern_x) == len(pattern_y), (
        "X has {} items while Y has {} items".format(
            len(pattern_x), len(pattern_y)))
    fields = ['_callback_str', 'name', '_regex']
    for i in range(len(pattern_x)):
        if not all(
            [getattr(pattern_x[i], field) == getattr(pattern_y[i], field)
             for field in fields]):
            raise AssertionError("The patterns are not equal")
    return True
