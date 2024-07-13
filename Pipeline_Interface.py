# def QAgent_setup():
#     try:
#         from .Configuration import *
#         from .MainFunctions.TestGenerator import *
#         from .MainFunctions.TestFix import *
#         from .MainFunctions.DecisionMaker import *
#         from .MainFunctions.BugFix import *

#         print("All imports successful!")
#         testGenerator = TestGenerator(GenUnitTestChain, db, globals())
#         testRegenerator = TestFix(
#             UnitTestFeedbackChain,
#             globals(),
#             True,
#         )
#         # judgeGenerator = DecisionMaker(judgeChain, globals())
#         bugFixGenerator = BugFix(bugFixChain, globals(), True)
#     except Exception as e:
#         print(e)
#         exit(-1)
def QAgent_product(code, description, testGenerator, testRegenerator, bugFixGenerator, judgeGenerator):
    # #TODO: IMPORTANT find a way to get the code and description from user later
    # for now they are hardcoded

    isCodeBuggy = True

    # print(isCodeBuggy)
    # isCodeBuggy is accessible here

    codeUnderTest, unitTestCode, feedbackParsed, testsToRepeat, isCodeBuggy = (
        testGenerator.generate(code, description, isCodeBuggy)
    )
    if (testGenerator.incompleteResponses == 1): # generate again
        codeUnderTest, unitTestCode, feedbackParsed, testsToRepeat, isCodeBuggy = (
            testGenerator.generate(code, description, isCodeBuggy)
        )
    
    print("Code Under Test: ", codeUnderTest)
    print("--------------------------------------------------------")
    print("Unit Test Code: ", unitTestCode)
    print("--------------------------------------------------------")
    print("Feedback Parsed: ", feedbackParsed)
    print("--------------------------------------------------------")
    print("Tests to Repeat: ", testsToRepeat)
    print("--------------------------------------------------------")
    bugFixedCode = "No bugs found in the code."
    print("befoooooooooooooooooooooooooooooreeeeeeeeeeeeeeeeeeeeeee")
    if feedbackParsed != '':
        
        isCodeBuggy, isTestCaseBuggy, explanation, isIncompleteResponse = judgeGenerator.generate(code, description, feedbackParsed)
        # but isCodeBuggy is not accessible here
        print(isCodeBuggy)
        print("*************************")
        if not isIncompleteResponse:
            if isCodeBuggy == 'True':
                bugFixedCode, unitTestCode, feedbackParsed, testsToRepeat = (
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
                print("tests to repeat", testsToRepeat)
            

    print("\n=============================================\nAfter Whichever: ")
    print("Code Under Test: ", codeUnderTest)
    print("Unit Test Code: ", unitTestCode)
    print("Feedback Parsed: ", feedbackParsed)
    print("Tests to Repeat: ", testsToRepeat)
    print("Bug Fixed: ", bugFixedCode)
    return unitTestCode,testsToRepeat,bugFixedCode
