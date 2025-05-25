from flask import Blueprint

bp = Blueprint('punch', __name__)

from app.punch import routes