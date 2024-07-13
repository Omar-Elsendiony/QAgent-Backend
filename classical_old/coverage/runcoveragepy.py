"""run coverage.py on the test file"""
import subprocess
from subprocess import PIPE
def run_coveragepy(project_path,test_file_name:str):
    p1 = subprocess.run(["coverage","run","--branch", f"{project_path}/classical/outputtests/{test_file_name}"], stderr=PIPE)
    json_report = subprocess.run(["coverage","json","--pretty-print","-o",f"{project_path}/classical/coverage/coverage.json",f"{project_path}/classical/outputtests/{test_file_name}"], stderr=PIPE)
    return p1,json_report

def final_report_html(project_path,test_file_name:str):
    html_report = subprocess.run(["coverage","html","-d",f"{project_path}/classical/coverage/html/",f"{project_path}/classical/outputtests/{test_file_name}"], stderr=PIPE)
    return html_report

#coverage run
#coverage run --branch  test.py
#coverage json test.py
#coverage json --pretty-print--show-contexts  test.py
#coverage annotate test.py