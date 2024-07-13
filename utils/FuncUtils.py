import re

# made according to human eval


def extractFunctionName(string):
    """Gets the function name from a function signature string."""
    # Define a regular expression pattern to match the function name
    pattern = r"def\s+(\w+)\s*\(.*\)"

    # Use re.match() to search for the pattern in the string
    match = re.match(pattern, string)

    # If a match is found, return the function name
    if match:
        return match.group(1)
    else:
        return None


# gets the function name from the function definition in human eval
def getFunctionName(funcDefinition):
    rs = re.search(r"\"\"\".*\"\"\"", funcDefinition, re.DOTALL)
    if rs == None:
        rs = re.search(r"\'\'\'.*\'\'\'", funcDefinition, re.DOTALL)

    allMatches = re.findall(r"def ", funcDefinition)
    if len(allMatches) == 1:
        end = rs.span()[0]
        funcHeader = funcDefinition[:end]
        UtilityFunction = ""
    else:
        *_, last = re.finditer(r"def ", funcDefinition)
        begin = last.span()[0]
        secondPart = funcDefinition[begin:]
        rs = re.search(r"\"\"\".*\"\"\"", secondPart, re.DOTALL)
        if rs == None:
            rs = re.search(r"\'\'\'.*\'\'\'", secondPart, re.DOTALL)
        end = rs.span()[0]
        funcHeader = funcDefinition[begin : end + begin]
        UtilityFunction = funcDefinition[:begin]
    return funcHeader, UtilityFunction


# replace function name if needed
def replaceFunctionName(string, replacement_string):
    # Define the regular expression pattern to match the function name
    pattern = r"def\s+(\w+)\s*"

    # Use re.sub() to replace the pattern with the replacement string
    modified_string = re.sub(pattern, "def " + replacement_string, string)

    return modified_string


def getTestCase(splitLines, errorChunck):
    lineNoGroup = re.search(r"(?<=line )(\d)+", errorChunck)
    lineNo = lineNoGroup.group(0)  # line number of the end of the error

    def getStartTestCase(splitLines, startIndex):
        for i in range(startIndex, 0, -1):
            if splitLines[i].find("def test") != -1:
                return i
        return -1

    startCaseIndex = getStartTestCase(splitLines, int(lineNo))
    testCase = "\n".join(splitLines[startCaseIndex : int(lineNo)])
    return testCase


def replace_input(code):
    # find all the lines that have input() in them
    lines = code.split("\n")
    variableNames = []
    # find the variable name on the left hand side of the assignment
    variablematches = re.finditer(r"(.+?)\s*=\s*input\(\)\s*", code)
    for matcher in variablematches:
        variableNames.append(matcher.group(1).strip())
    functionheader = "def myfunc(" + ",".join(variableNames) + "):"
    # replace any line containing input with ""
    for i in range(len(lines)):
        if "input()" in lines[i]:
            lines[i] = ""
        lines[i] = "\t" + lines[i]

    # add function header and format code
    code = functionheader + "\n" + "\n".join(lines)
    return code
