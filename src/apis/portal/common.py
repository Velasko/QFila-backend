from flask_restx import inputs

from .app import ns

pagination = ns.parser()
pagination.add_argument("page", type=int, default=1)
pagination.add_argument("pagesize", type=int, default=15)

force = ns.parser()
force.add_argument('force', type=inputs.boolean,
	help="Will force the operation if parsed"
)