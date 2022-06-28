import database
import fibon
from database import get_connection


def prompt_user_input():

    fib_number = int(input("What number should the fibonaci sequence be calculated for? "))

    return fib_number


def run_app():
    fib = prompt_user_input()

    with get_connection() as connection:
        database.create_table(connection)
        fib_db = database.check_if_fib_already_computed(connection, fib)

        if fib_db:
            print(f"\nreturned from the database: {fib_db}")
        else:
            result = fibon.fib(fib)
            print(f"\n{result}")
            database.insert_fb_into_db(connection, fib, result)


ACTIONS = {
    "1": run_app,
    "2": database.clear_db_table,
    "3": database.show_top_ones,
}

OPTIONS = """
1) Run app
2) Clear fibonaci database table
3) Show top 10 searched
4) Quit
"""


def actions_prompt():

    while (action := input(OPTIONS)) != "4":
        try:
            ACTIONS[action]()
        except KeyError:
            print("Invalid Key")


if __name__ == "__main__":
    actions_prompt()
