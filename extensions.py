from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

mail = Mail()
limiter = Limiter(key_func=get_remote_address)

