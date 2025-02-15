import sys
import argparse
from flask import Flask
from dataAccess.database.database import init_db, User, _db as db


def create_user(
    username: str, password: str, app: Flask = None, create_db: bool = True
):
    if app is None:
        app = Flask(__name__)
    with app.app_context():
        if create_db:
            init_db(app)

        if db.session.query(User).filter_by(username=username).first():
            print("User already exists.")
            sys.exit(1)

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print("User created successfully.")


def set_password(username: str, new_password: str, app: Flask = None):
    if app is None:
        app = Flask(__name__)
    with app.app_context():
        init_db(app)
        user = db.session.query(User).filter_by(username=username).first()
        if user:
            user.password = new_password
            db.session.commit()
            print("Password updated successfully.")
        else:
            print("User not found.")
            sys.exit(1)


def delete_user(username: str, app: Flask = None):
    if app is None:
        app = Flask(__name__)
    with app.app_context():
        init_db(app)
        user = db.session.query(User).filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            print("User deleted successfully.")
        else:
            print("User not found.")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User management script.")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new user.")
    create_parser.add_argument(
        "username", type=str, help="The username for the new user."
    )
    create_parser.add_argument(
        "password", type=str, help="The password for the new user."
    )

    set_password_parser = subparsers.add_parser(
        "set_password", help="Set a new password for an existing user."
    )
    set_password_parser.add_argument(
        "username", type=str, help="The username of the user."
    )
    set_password_parser.add_argument(
        "password", type=str, help="The new password for the user."
    )

    delete_parser = subparsers.add_parser("delete", help="Delete an existing user.")
    delete_parser.add_argument(
        "username", type=str, help="The username of the user to delete."
    )

    args = parser.parse_args()

    if args.command == "create":
        create_user(args.username, args.password)
    elif args.command == "set_password":
        set_password(args.username, args.new_password)
    elif args.command == "delete":
        delete_user(args.username)
