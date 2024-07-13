from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_community.chat_models.huggingface import ChatHuggingFace
import openai
from utils.PreprocessUtils import addMixtralTokens


repair_code_template2 = """You are a python expert in solving bugs:
Given the following python code, its description, a test case that produce an error, the error message.
Knowing that the python code under test is buggy.
You are required to repair the code under test to be bugless and make sure that the functionality conform with the description provided.

Method under test:
{code}

Description:
{description}

test case that produces an error:
{test_case_error}

the error message:
{error_message}

You follow my rules and orders and if you do not know the answer, don't make things UP!
You are going to follow the criteria that I give to you.
Criteria:
1. Understand the description and the python code under test.
2. Interpret the test case that produces an error and the accompanying error message.
3. Repair the code under test to be bug-free.
4. Make sure that the functionality of the repaired code conforms to the description.

Your answer is a list of bugs found and the repaired code only.
The repaired code should be a markdown code snippet formatted in the following schema, including the leading and trailing "```python" and "```" respectively:"""

repair_code_with_fewShots_template2 = """You are a python expert in solving bugs:
Given the following python code, its description, a test case that produce an error, the error message and an explanation of a judge why the error is in the code under test.
knowing that a fair judge decided that the python code under test is buggy.
You are required to repair the code under test to be bugless and make sure that the functionality conform with the description provided.

Method under test:
{code}

Description:
{description}

the error message:
{error_message}

Explanation of a judge why the error is in the code under test:
{explanation}

I am going to provide you similar buggy functions and their corresponding bug fixes that you may need to use in your tests.
{test_cases_of_few_shot}

You follow my rules and orders and if you do not know the answer, don't make things UP!
You are going to follow the criteria that I give to you.
Criteria:
1. Understand the description and the python code under test.
2. Interpret the test case that produces an error and the accompanying error message.
3. Understand the explanation of a judge for why the error is in the code under test.
3. Repair the code under test to be bug-free.
4. Make sure that the functionality of the repaired code conforms to the description.

Your answer is a list of bugs found and the repaired code only.
The repaired code should be a markdown code snippet formatted in the following schema, including the leading and trailing "```python" and "```" respectively:"""

###################### SECOND CASES ##########################
repair_code_template = """You are a python expert in solving bugs:
Given the following python code, its description, a test case that produce an error, the error message.
Knowing that the python code under test is buggy.
You are required to repair the code under test to be bugless and make sure that the functionality conform with the description provided.
Method under test:
{code}

Description:
{description}

test case that produces an error:
{test_case_error}

the error message:
{error_message}


Understand the description and the python code under test.
Interpret the test case that produces an error and the accompanying error message.
Understand the explanation of a judge for why the error is in the code under test.
Repair the code under test to be bug-free.

Your answer is a list of bugs found and the repaired code only.
The repaired code should be a markdown code snippet formatted in the following schema, including the leading and trailing "```python" and "```" respectively:"""

repair_code_with_fewShots_template = """You are a python expert in solving bugs:
Given the following python code, its description, a test case that produce an error, the error message and an explanation of a judge why the error is in the code under test.
knowing that a fair judge decided that the python code under test is buggy.
You are required to repair the code under test to be bugless and make sure that the functionality conform with the description provided.
Method under test:
{code}

Description:
{description}

the error message:
{error_message}

Explanation of a judge why the error is in the code under test:
{explanation}

I am going to provide you similar buggy functions and their corresponding bug fixes that you may need to use in your tests.
{test_cases_of_few_shot}

Understand the description and the python code under test.
Interpret the test case that produces an error and the accompanying error message.
Understand the explanation of a judge for why the error is in the code under test.
Repair the code under test to be bug-free.

Your answer is a list of bugs found and the repaired code only.
The repaired code should be a markdown code snippet formatted in the following schema, including the leading and trailing "```python" and "```" respectively:"""




def InitializeBugFixChain(llm, fewshots=False):
    global repair_code_template
    global repair_code_with_fewShots_template
    # adding [INST] to mixtral manually
    if isinstance(llm, HuggingFaceHub) and "Mixtral" in llm.repo_id:
        repair_code_template = addMixtralTokens(repair_code_template)
        repair_code_with_fewShots_template = addMixtralTokens(
            repair_code_with_fewShots_template
        )
    if not fewshots:
        Bug_Fix_Template = PromptTemplate(
            template=repair_code_template,
            input_variables=[
                "description",
                "code",
                "test_case_error",
                "error_message",
            ],
            verbose=False,
        )
    else:
        Bug_Fix_Template = PromptTemplate(
            template=repair_code_with_fewShots_template,
            input_variables=["description", "code", "test_cases_of_few_shot"],
            verbose=False,
        )

    BugFixChain = LLMChain(llm=llm, verbose=False, prompt=Bug_Fix_Template)
    return BugFixChain
