from nanowire_service_py import Logger  # type: ignore


def test_logger():
    log = Logger()
    log.track("test-uuid")

    log.info("Hello {name}", name="test")
    log.debug("Hello {name}", name="test")
    log.success("Hello {name}", name="test")
    log.warning("Hello {name}", name="test")
    log.error("Hello {name}", name="test")
    log.critical("Hello {name}", name="test")
    try:
        raise Exception("Hello")
    except Exception as e:
        log.exception(e)

    assert len(log.consume_logs()) == 7
