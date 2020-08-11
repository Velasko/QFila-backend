import argparse

from sqlalchemy import create_engine

from .scheme import Base


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Declaration of the database scheme of the aplication')
	parser.add_argument('--database', default='sqlite:///sqlalchemy_example.db',
						type=str, help="Which database the script should run on.")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--create_scheme', action='store_true', help="Generates the scheme inside the database.")
	group.add_argument('--delete_scheme', action='store_true', help="Deletes the scheme inside the database.")

#	insert = parser.add_subparser("insert")#database insert parser

	args = parser.parse_args()

	print(args.database)

	if args.create_scheme:
		engine = create_engine(args.database)
		Base.metadata.create_all(engine)
		print("scheme created")
	elif args.delete_scheme:
		raise NotImplemented("Deletion of scheme not implemented.")
	else:
		parser.print_help()