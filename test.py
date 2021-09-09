from nanowire_service_py import Logger  # type: ignore

log = Logger()
log.track("Test")
log.debug("Hello {name}", name="test")
log.success("Hello {name}", name="test")
log.warning("Hello {name}", name="test")
log.error("Hello {name}", name="test")
log.critical("Hello {name}", name="test")
try:
    raise Exception("Hahah")
    # log.exception("failed")
except Exception as e:
    log.exception(e)
logs = log.consume_logs()
print([log.level for log in logs])
