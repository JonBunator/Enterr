import sys
import argparse
from dataAccess.database.database import init_db, User, get_db_session


def create_user(username: str, password: str, create_db: bool = True):

    if create_db:
        init_db()
    with get_db_session() as session:
        if session.query(User).filter_by(username=username).first():
            print("User already exists.")
            if create_db:
                sys.exit(1)
            else:
                return

        user = User(username=username, password=password)
        session.add(user)
        session.commit()
        print("User created successfully.")


def set_password(username: str, new_password: str):
    init_db()
    with get_db_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            session.commit()
            print("Password updated successfully.")
        else:
            print("User not found.")
            sys.exit(1)


def delete_user(username: str):
    init_db()
    with get_db_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
            print("User deleted successfully.")
        else:
            print("User not found.")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User management script.")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create_user", help="Create a new user.")
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

    delete_parser = subparsers.add_parser(
        "delete_user", help="Delete an existing user."
    )
    delete_parser.add_argument(
        "username", type=str, help="The username of the user to delete."
    )

    args = parser.parse_args()

    if args.command == "create_user":
        create_user(args.username, args.password)
    elif args.command == "set_password":
        set_password(args.username, args.password)
    elif args.command == "delete_user":
        delete_user(args.username)
