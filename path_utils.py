def fix_sys_path():
    try:
        import dev_appserver
        if not hasattr(dev_appserver, 'fix_sys_path'):
            raise SystemExit(
                "PYTHONPATH contains an invalid dev_appserver, please locate a version with `fix_sys_path`")
        dev_appserver.fix_sys_path()
    except ImportError:
        raise SystemExit("Please make sure the App Engine SDK is in your PYTHONPATH.")
