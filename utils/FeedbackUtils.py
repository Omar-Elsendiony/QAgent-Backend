###### This file contains the functions to parse the feedback from running the code and extract the relevant information from it. ######

import re


# gets feedback from running the code using exec
# empty in case of success
def getFeedbackFromRun(response):
    """
    An example parsed feedback is:

    "FAIL: test_add (test_module.TestClass)
    ----------
    Traceback (most recent call last):
    File "test_module.py", line 6, in test_add
        self.assertEqual(add(2, 3), 5)
    FAIL: test_sub (test_module.TestClass)
    .....etc"
    """
    lines = response.split("\n")
    feedback = ""
    in_failmessage = False
    if lines[0].startswith("F") or lines[0].startswith(".") or lines[0].startswith("E"):
        for i, line in enumerate(lines):
            if line.startswith("FAIL") or line.startswith("ERROR"):
                in_failmessage = True
                feedback += line + "\n"
            elif line.startswith("--"):
                if lines[i + 1].startswith("Ran"):
                    return feedback

            elif in_failmessage == True:
                if line.startswith("=="):
                    continue
                if i == len(lines) - 1:
                    return feedback
                feedback += line + "\n"
        return feedback
    else:
        return response


def getFeedbackFromRunList(response):  # omar's version
    lines = response.split("\n")
    in_failmessage = False
    feedbacks = []
    for i, line in enumerate(lines):
        if line.startswith("FAIL") or line.startswith("ERROR"):
            feedback = ""
            in_failmessage = True
            feedback += line + "\n"
        elif line.startswith("--"):
            if lines[i + 1].startswith("Ran"):
                if feedback != "":
                    feedbacks.append(feedback)
                return feedbacks

        elif in_failmessage == True:
            if line.startswith("=="):
                if feedback != "":
                    feedbacks.append(feedback)
                    feedback = ""
                    continue
            if i == len(lines) - 1:
                if feedback != "":
                    feedbacks.append(feedback)
                return feedbacks
            feedback += line + "\n"


def getNumNonSucceedingTestcases(feedback):
    """Finds the number of Ran Tests and Failures"""
    failures_match = re.search(r"failures=(\d+)", feedback)
    errors_match = re.search(r"errors=(\d+)", feedback)
    # Extract the numbers or default to 0 if not found
    failures = int(failures_match.group(1)) if failures_match else 0
    errors = int(errors_match.group(1)) if errors_match else 0

    return failures, errors


def getNonSucceedingTestcases(feedback):
    """Gets the names of the failed test cases functions"""
    failed_tests = re.findall(r"FAIL: (.*) \(", feedback)
    error_tests = re.findall(r"ERROR: (.*) \(", feedback)
    return {"failed": failed_tests, "error": error_tests}


def getNumAssertions(code_text):
    total_num = len(re.findall(r"self\.assert.", code_text, flags=re.MULTILINE))
    return total_num


# gets whole feedback and returns the error message
def getOneError(feedback):
    match = re.search(r"(ERROR|FAIL):(.)+?(ERROR|FAIL)", feedback, re.DOTALL)
    if match is None:
        match = re.search(r"(ERROR|FAIL):(.)+", feedback, re.DOTALL)
        if match is None:
            # syntax error case
            return feedback
    ErrorText = match.group(0)
    ErrorText = ErrorText[:-6]
    return ErrorText
