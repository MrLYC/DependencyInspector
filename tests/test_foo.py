from dependency_inspector.provider import foo


def test_foo():
    assert foo() == "foo"
