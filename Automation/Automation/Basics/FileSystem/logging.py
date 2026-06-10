import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO
)

information = "information"
error = "error"
warning = "warning"
critical = "critical"

logging.info(information)
logging.error(error)
logging.warning(warning)
logging.critical(critical)

