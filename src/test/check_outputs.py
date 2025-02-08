import sys

def raise_if_not_equal(expected, actual, variable_name):
    if expected != actual:
        raise Exception(f"Expected {variable_name} to be {expected}, but got {actual}")

def check_outputs(short_version, long_version, last_version):
    expected_short_version = "3.0.4"
    expected_long_version = "v3.0.4"
    expected_last_version = "v3.0.0"
    raise_if_not_equal(expected_short_version, short_version, "short_version")
    raise_if_not_equal(expected_long_version, long_version, "long_version")
    raise_if_not_equal(expected_last_version, last_version, "last_version")

if __name__ == "__main__":
    short_version = sys.argv[1]
    long_version = sys.argv[2]
    last_version = sys.argv[3]
    check_outputs(short_version, long_version, last_version)