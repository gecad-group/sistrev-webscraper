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
    deleteAllProjects()
    n_proj_prev = len(asreview.project.get_projects())

    proj = createProject("Test Project")
    proj.add_dataset('./testdata/artf-intl-wos.ris')

    print(f"{n_proj_prev} to {len(asreview.project.get_projects())}")

    # proj.add_dataset(os.getcwd()+'\\out.ris')

    p = Process(target=LABEntryPoint.execute, args=(LABEntryPoint(), []))
    p.start()

    # while project review is not finished
    while proj.reviews[0].status != "finished":
        time.sleep(5)
        proj = asreview.project.ASReviewProject(proj.project_path, proj.project_id)
