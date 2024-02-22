"""Python script to track time"""

import sqlite3
from datetime import datetime, timedelta
from tabulate import tabulate


class TimeTrack:
    """Class to keep track of tasks and times"""

    def __init__(self):
        self.current_task = None
        self.start_time = None
        self.con = sqlite3.connect("time_track.db")
        self.cur = self.con.cursor()
        self.todays_date = datetime.now().strftime("%Y_%m_%d")
        table = f"""CREATE TABLE IF NOT EXISTS reported_time_{self.todays_date}(
            project, start_time, end_time, total_time
            )
            """
        self.cur.execute(table)
        self.con.commit()

    def start_task(self, task):
        """Function to start a task or summarize the day"""
        while True:
            try:
                task = int(task)
                if task == 0:
                    self.read_and_summarize_tasks()
                    self.exit()
                    return False
                if self.current_task:
                    print("A task is already in progress.")
                    return True
                if task not in get_tasks():
                    print("No task with that number")
                    task = input("Enter a correct number: ")
                else:
                    self.current_task = get_tasks()[task]
                    self.start_time = datetime.now()
                    print(
                        f"Task '{self.current_task}' started at "
                        f"{self.start_time.strftime('%H:%M')}."
                    )
                    return True
            except ValueError:
                print("Please enter a valid integer number.")
                task = input("Enter a correct number: ")

    def stop_task(self):
        """Function to stop active task"""
        if not self.current_task:
            print("No task is currently in progress.")
        else:
            end_time = datetime.now()
            elapsed_time = end_time - self.start_time
            print(
                f"Task '{self.current_task}' stopped at {end_time.strftime('%H:%M')}."
            )
            print(f"Elapsed time: {elapsed_time}")
            print()

            # Write task, start_time and end_time to db
            task_start_end = f"""
                INSERT INTO reported_time_{self.todays_date} VALUES
                    ('{self.current_task}', '{self.start_time}', '{end_time}', '{elapsed_time}')
                """
            self.cur.execute(task_start_end)
            self.con.commit()

            self.current_task = None
            self.start_time = None
        return True

    def read_and_summarize_tasks(self):
        """Function to summarize the time for each task in the database"""

        query = f"SELECT project, SUM(strftime('%s', end_time) - strftime('%s', start_time)) \
            AS total_time FROM reported_time_{self.todays_date} GROUP BY project"
        self.cur.execute(query)
        rows = self.cur.fetchall()

        # Convert total_time from seconds to HH:MM format
        formatted_rows = [(row[0], str(timedelta(seconds=row[1]))) for row in rows]

        # Print the results using tabulate
        headers = ["Task", "Total Time (HH:MM:SS)"]
        print(tabulate(formatted_rows, headers=headers, tablefmt="grid",colalign=("left", "right")))

    def exit(self):
        """Function to close connection to database"""
        self.con.close()


def show_tasks():
    """Get all tasks and print them"""
    tasks = get_tasks()
    print("Tasks:")
    for option, task in tasks.items():
        print(f"{option}: {task:<20}", end="\t" if option % 4 != 0 else "\n")
    print()

    return tasks


def get_tasks():
    """Function that holds all tasks"""

    with open("tasks", "r") as file:

        tasks = {0: "Exit", **{i: line.strip() for i, line in enumerate(file, start=1) if line.strip()}}

    return tasks


if __name__ == "__main__":
    print()
    todays_worker = TimeTrack()
    while True:
        show_tasks()
        print()
        print("What do you work with? (Enter 0 to sumerize the day and exit)")
        try:
            working_with = int(input(": "))
            if not todays_worker.start_task(working_with):
                break
        except ValueError:
            print("Please use a number corresponding to the task")
            print()
            continue

        input("Press Enter when done with the task...")
        todays_worker.stop_task()
