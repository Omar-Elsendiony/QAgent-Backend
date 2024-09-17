from flask_cors import CORS  # import flask_cors
from flask import Flask, request, jsonify
app = Flask(__name__)
from Pipeline_Interface import QAgent_product
from Configuration import *
from MainFunctions.TestGenerator import *
from MainFunctions.TestFix import *
from MainFunctions.DecisionMaker import *
from MainFunctions.BugFix import *
from classical.main import main_for_api

from DBRet.test import *
CORS(app)  # enable CORS


# region QAgent
def setupQAgent():
    try:
        print("All imports successful!")
        testGenerator = TestGenerator(GenUnitTestChain, "", globals())
        testRegenerator = TestFix(
            UnitTestFeedbackChain,
            globals(),
            True,
        )
        judgeGenerator = DecisionMaker(judgeChain, globals())
        bugFixGenerator = BugFix(bugFixChain, globals(), True)
        return testGenerator, testRegenerator, bugFixGenerator, judgeGenerator
    except Exception as e:
        print(e)
        exit(-1)


testGenerator, testRegenerator, bugFixGenerator, judgeGenerator = setupQAgent()


@app.route('/qagentai', methods=['POST'])
def run_python():
    code = request.json.get('code')
    description = request.json.get('description')
    if code:
        try:
            # execute the main function
            print("Running QAgentAI")
            result = QAgent_product(
                code, description, testGenerator, testRegenerator, bugFixGenerator, judgeGenerator)
            # print(result)
            return jsonify({'output': list(result)})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No code provided'}), 400

#endregion


@app.route('/query', methods=['POST'])
def query():
    try:
        print(request.json)
        code = request.json['code']
        programmingLangugae=request.json['language']
        print(programmingLangugae)
        if programmingLangugae=='python':
            isPython=True
            isJava=False
        elif programmingLangugae=='java':
            isPython=False
            isJava=True
        else:
            isPython=False
            isJava=False
        thresholdSameLanguage = request.json['thresholSameLang']
        thresholdDifferentLanguage = request.json['thresholdDiffLang']
        codes, tests = query_db(code,isJava,isPython,thresholdSameLanguage,thresholdDifferentLanguage)
        # print("codes is", codes)
        if len(codes) == 0:
            return jsonify({"codes":["No similar code found"], "tests": [{"test 0":"No similar code found"}]})
        return jsonify({'codes': codes, 'tests': tests})
    except Exception as e:
        return jsonify({"error": str(e)})




@app.route('/run-classical', methods=['POST'])
def generate_classical():
    code = request.json.get('code')
    print(code)
    if code:
        try:
            result = main_for_api(code)
            print(result)
            return jsonify({'output': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No code provided'}), 400






if __name__ == '__main__':
    # app.run(port=8080,debug=True, use_reloader=False)
    app.run(port=8000)

