import os
import shutil
import time
from multiprocessing import Process
from pathlib import Path
import asreview
from asreview.entry_points import LABEntryPoint
import uuid


def deleteAllProjects():
    for project in asreview.project.get_projects():
        shutil.rmtree(project.project_path)

def createProject(name: str = "", id: str = "") -> asreview.project.ASReviewProject:
    if len(id) == 0:
        id = uuid.uuid4().hex

    if len(name) == 0:
        name = id

    return asreview.project.ASReviewProject.create(Path(asreview.utils.asreview_path(), id), project_id=id, project_name=name)

def launch_interface() -> Process:
    p = Process(target=LABEntryPoint.execute, args=(LABEntryPoint(), []))
    p.start()

    return p


if __name__ == '__main__':
    name = input("What name should we give the project? ")

    proj = createProject(name)

    print("What is the path of the dataset(s) to import? (Press ENTER with empty input to terminate)")
    f = input(": ")
    while (len(f) > 0):
        proj.add_dataset(os.path.abspath(f))
        f = input(": ")

    # proj.add_dataset(os.getcwd()+'\\out.ris')

    p = Process(target=LABEntryPoint.execute, args=(LABEntryPoint(), []))
    p.start()

    time.sleep(15)
    input("Press ENTER to end program. You need to close the browser tab manually!")
    p.kill()