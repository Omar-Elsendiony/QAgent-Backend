import re


# TODO : rage3 aslun m7tageen el file da wla la2?
class Regeneration:

    def __init__(self, chat_model) -> None:
        self.chat_model_arb = chat_model

    def updateUnittest(self, code, tc):
        updatetestcase = f"""
        Make this test case:
        {tc}

        replace the one in the following code:
        {code}


        Generate the whole code after replacement and it should be encloded by ```python and ```
        Preserve the indentation correctness in the response.
        """
        res = (self.chat_model_arb.invoke(updatetestcase)).content
        return res

    def regeneratePrompt(self, code, description, testcase, feedback):
        reGenerationPrompt = f"""
you generated unittest for the following method under test having the following description:
*Method under test*:
{code}

*Description*:
{description}


but this test failed
*Test*:
{testcase}

with the following feedback:
*Feedback*:
{feedback}

Take the two values that are being compared in the assertion above and check if the expected value is correct.
Consider that the assertion may be a negative test that makes sure that the invalid behaviour is tested.
Change either the test case or the assertion (if any of them is incorrect) and explain your thought process in changing the value if any.
Generate only the fixed test case enclosed by ```python and ``` to be able to run the code and re-run the code.
        """

        res = self.chat_model_arb.invoke(reGenerationPrompt)
        if res:
            res = res.content
        return res

    # # made according to mixtral response
    # def get_code_from_response(self, response):
    #     # has backticks in different positions
    #     response = re.sub(r"```python```", "", response)
    #     response = re.sub(r"```python and ```", "", response)

    #     """ find all instances of ```python and start from the last one"""
    #     s = re.finditer(r"```python", response)
    #     for st in s:
    #         startIndex = st.span(0)[0]
    #     response = response[startIndex:]

    #     code = re.search(r"[^\"](?<=```python\n)(.*)\)\n(?=```)", response, re.DOTALL)
    #     if code is None:
    #         code = re.search(
    #             r"[^\"](?<=```python\n)(.*)\)\n\n(?=```)", response, re.DOTALL
    #         )
    #     if code is None:
    #         code = re.search(r"[^\"](?<=```python\n)(.*)\)(?=```)", response, re.DOTALL)
    #     if code is None:
    #         code = re.search(r"[^\"](?<=```python\n)(.*)", response, re.DOTALL)
    #     # print(code.group(0))
    #     if code is None:
    #         return response[startIndex:]
    #     return code.group(0) if code is not None else None

    # def getTestCase(self, splitLines, errorChunck):
    #     lineNoGroup = re.search(r"(?<=line )(\d)+", errorChunck)
    #     lineNo = lineNoGroup.group(0)  # line number of the end of the error

    #     def getStartTestCase(splitLines, startIndex):
    #         for i in range(startIndex, 0, -1):
    #             if splitLines[i].find("def test") != -1:
    #                 return i
    #         return -1

    #     startCaseIndex = getStartTestCase(splitLines, int(lineNo))
    #     testCase = "\n".join(splitLines[startCaseIndex : int(lineNo) + 2])
    #     return testCase


#     def get_feedback(
#         self,description,code,codeRan,feedback_test,getFeedbackFromRunList,
#     ):
#         def substituteTestCases(old, new, codeRan):
#             new = re.sub(r"\n {4}([^d ])", r"\n        \1", new)
#             new = re.sub(r"with(.*)\n {8}([^s|w])", r"with\1\n            \2", new)
#             if not new.startswith(" "):
#                 new = "    " + new
#             codeRan = re.sub(rf"{re.escape(old)}", rf"{new}", codeRan)
#             return codeRan

#         explanationFile = open("FeedbackOutput/" + "explanation.txt", "a")

#         splitLines = codeRan.split("\n")
#         feedback_l = getFeedbackFromRunList(feedback_test)
#         if feedback_l is None:
#             return None
#         for f in feedback_l:
#             # print("before:")
#             before = self.getTestCase(splitLines, f)
#             afterX = self.regeneratePrompt(code, description, before, f)
#             print(afterX)
#             explanationFile.write(afterX)
#             explanationFile.write("\n=========================================\n")
#             after = self.get_code_from_response(afterX)
#             matched = re.search(r"def test", after, re.DOTALL)
#             # if (matched is None):
#             #     print(afterX)
#             #     continue
#             start = matched.span()[0]
#             matched = re.search(r"```", after, re.DOTALL)
#             if matched is None:
#                 after = after[start:]
#             else:
#                 after = after[start : matched.span()[0]]

#             after = re.sub(r"\\'", r"\'", after)
#             # after = re.sub(r"\\", r"\'", after)
#             codeRan = substituteTestCases(before, after, codeRan)

#         fix_unit = f"""
# Remove the lines that are incorrect in the following unit test and replace them with the correct lines if needed:
# {codeRan}

# The output code should be encloded by ```python and ```
#         """
#         # res = (self.chat_model_arb.invoke(fix_unit)).content
#         # codeRan = self.get_code_from_response(res)
#         explanationFile.close()
#         return codeRan
