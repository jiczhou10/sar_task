import time
import webbrowser
import tkinter
from tkinter import *
from datetime import datetime
import os
import csv
import glob
from random import randint

from env_generator import path_generator
from env_generator.path_generator import create_builder_task1, create_builder_task2, create_builder_tutorial
from matrx_visualizer import visualization_server



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # root = Tk()
    # root.title('Choose task')
    # root.attributes("-fullscreen", True)
    # choice = IntVar()
    # text = Text(height=8, width=100, font=("Arial", 30), bg="#00A6D6", fg="#FFFFFF", highlightthickness=0,
    #             borderwidth=0)
    # text.tag_configure("center", justify="center")
    # text.insert("1.0", "Welcome! \n \n Please pick one of these three scenario's:")
    # text.tag_add("center", "1.0", "end")
    # text.pack(pady=20)
    # tutorial = Button(root, text="Tutorial", command=lambda: [choice.set(0), root.destroy()], font=("Arial", 30))
    # tutorial.pack(pady=20)
    # task1 = Button(root, text="Task A", command=lambda: [choice.set(1), root.destroy()], font=("Arial", 30))
    # task1.pack(pady=20)
    # task2 = Button(root, text="Task B", command=lambda: [choice.set(2), root.destroy()], font=("Arial", 30))
    # task2.pack(pady=20)
    # root.mainloop()
    # url = "http://127.0.0.1:3000/human-agent/human"
    # webbrowser.get().open(url)
    # scenario = choice.get()
    # path_generator.run(scenario)
    rnd_seed = randint(0, 1)
    print('rnd number: ', rnd_seed)
    print("\nEnter the type of task: ")
    choice = input()
    if choice == 'tutorial':
        builder = create_builder_tutorial()

    if choice == 'task1':
        # if rnd seed is 0, first play with sar_agent_1
        builder = create_builder_task1(rnd=rnd_seed)

    elif choice == 'task2':
        print("\nEnter the rnd_number for first task: ")
        rnd_number = input()
        # if rnd_seed == 0:
        #     rnd_seed = 1
        # else:
        #     rnd_seed = 0
        second_rnd_seed = 1
        # if rnd_number == 0:
        #     second_rnd_seed = 1
        if rnd_number == 1:
            second_rnd_seed = 0
        # rnd seed 0: with basic agent
        # rnd seed 1: with additional agent
        builder = create_builder_task2(second_rnd_seed)
    media_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
    # Start the MATRX API we need for our visualisation
    builder.startup(media_folder=media_folder)
    vis_thread = visualization_server.run_matrx_visualizer(verbose=False, media_folder=media_folder)
    # Create a world
    world = builder.get_world()
    # Run that world (and visit http://localhost:3000)
    world.run(api_info=builder.api_info)
    fld = os.getcwd()
    print('fld', fld)
    # We can use the function glob.glob()
    # to retrieve paths recursively from inside the directories/files and subdirectories/subfiles.
    # max(, key)
    # It refers to the single argument function to customize the sort order.
    # The function is applied to each item on the iterable.
    recent_dir = max(glob.glob(os.path.join(fld, '*/')), key=os.path.getmtime)
    print('1st recend dir ', recent_dir)
    recent_dir = max(glob.glob(os.path.join(recent_dir, '*/')), key=os.path.getmtime)
    print('2nd recend dir ', recent_dir)

    action_file = glob.glob(os.path.join(fld, 'world_1/action*'))[0]
    message_file = glob.glob(os.path.join(fld, 'world_1/message*'))[0]

    action_header = []
    action_contents = []
    message_header = []
    message_contents = []
    unique_agent_moves = []
    unique_human_moves = []
    dropped_human = []
    dropped_agent = []

    safe_zones = [(17, 25), (18, 25), (19, 25), (20, 25), (21, 25), (22, 25), (23, 25), (24, 25), (25, 25),
                  (17, 26), (18, 26), (19, 26), (20, 26), (21, 26), (22, 26), (23, 26), (24, 26), (25, 26),
                  (17, 27), (18, 27), (19, 27), (20, 27), (21, 27), (22, 27), (23, 27), (24, 27), (25, 27)]

    with open(action_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in reader:
            if action_header == []:
                action_header = row
                continue
            if row[1:3] not in unique_agent_moves:
                unique_agent_moves.append(row[1:3])
            if row[3:5] not in unique_human_moves:
                unique_human_moves.append(row[3:5])
            if row[1] == 'DropObject' and row[1:3] not in dropped_agent and row[2] in safe_zones:
                dropped_agent.append(row[1:3])
            if row[3] == 'DropObject' and row[3:5] not in dropped_human and row[4] in safe_zones:
                dropped_human.append(row[3:5])
            res = {action_header[i]: row[i] for i in range(len(action_header))}
            action_contents.append(res)

    with open(message_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in reader:
            if message_header == []:
                message_header = row
                continue
            res = {message_header[i]: row[i] for i in range(len(message_header))}
            message_contents.append(res)

    no_messages_human = message_contents[-1]['total_number_messages_human']
    no_messages_agent = message_contents[-1]['total_number_messages_agent']
    mssg_len_human = message_contents[-1]['average_message_length_human']
    mssg_len_agent = message_contents[-1]['average_message_length_agent']
    no_ticks = action_contents[-1]['tick_nr']
    success = action_contents[-1]['done']
    print("Saving output...")
    with open(os.path.join(recent_dir, 'world_1/output.csv'), mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(
            ['completed', 'no_ticks', 'moves_agent', 'moves_human', 'no_messages_agent', 'no_messages_human',
             'message_length_agent', 'message_length_human', 'victims_dropped_agent', 'victims_dropped_human'])
        csv_writer.writerow(
            [success, no_ticks, len(unique_agent_moves), len(unique_human_moves), no_messages_agent,
             no_messages_human,
             mssg_len_agent, mssg_len_human, len(dropped_agent), len(dropped_human)])

    # url = "http://127.0.0.1:3000/human-agent/human"
    # webbrowser.get().open(url)

    builder.stop()