try:
    from Configuration import *
    from MainFunctions.TestGenerator import *
    from MainFunctions.TestFix import *
    from MainFunctions.DecisionMaker import *
    from MainFunctions.BugFix import *

    print("All imports successful!")
    testGenerator = TestGenerator(GenUnitTestChain, db, globals())
    testRegenerator = TestFix(
        UnitTestFeedbackChain,
        globals(),
        True,
    )
    # judgeGenerator = DecisionMaker(judgeChain, globals())
    bugFixGenerator = BugFix(bugFixChain, globals(), True)
except Exception as e:
    print(e)
    exit(-1)


# #TODO: IMPORTANT find a way to get the code and description from user later
# for now they are hardcoded


code = """def add(a, b):\n    return a - b \n"""

description = "This function adds two numbers"

isCodeBuggy = True

# print(isCodeBuggy)
# isCodeBuggy is accessible here

codeUnderTest, unitTestCode, feedbackParsed, testsToRepeat, isCodeBuggy = (
    testGenerator.generate(code, description, isCodeBuggy)
)
print("Code Under Test: ", codeUnderTest)
print("Unit Test Code: ", unitTestCode)
print("Feedback Parsed: ", feedbackParsed)
print("Tests to Repeat: ", testsToRepeat)


# but isCodeBuggy is not accessible here

if isCodeBuggy:
    codeUnderTest, unitTestCode, feedbackParsed, testsToRepeat = (
        bugFixGenerator.generate(
            description, codeUnderTest, unitTestCode, testsToRepeat, feedbackParsed
        )
    )
else:
    codeUnderTest, unitTestCode, feedbackParsed, testsToRepeat = (
        testRegenerator.generate(
            description, codeUnderTest, unitTestCode, feedbackParsed
        )
    )

print("\n=============================================\nAfter Whichever: ")
print("Code Under Test: ", codeUnderTest)
print("Unit Test Code: ", unitTestCode)
print("Feedback Parsed: ", feedbackParsed)
print("Tests to Repeat: ", testsToRepeat)
