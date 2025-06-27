

def test_import():
    try:
        import log4data as l4d
        assert True
    except Exception:
        assert False , "Couldn't import log4data"
