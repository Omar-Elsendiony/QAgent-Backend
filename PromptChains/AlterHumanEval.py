import openai
alterFunctionCodeTemplate = """You are a python expert and your task is: Given the following description and python code:
Description:
{description}
Code:
'''python
{code}'''
your task is to introduce bugs into the above correct python code. The bugs should include runtime errors and logical errors. 
Ensure that the introduced bugs deviate the code from its intended functionality described.
The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "```python" and "```" respectively:"""


#description,
def createPromptStringGenerateTest(
    description,code
):
    
    prompt = alterFunctionCodeTemplate.format(description=description, code=code)
    
    return prompt


def queryGptAlterCode(
    model, description, code
):
    prompt = createPromptStringGenerateTest(
        description,code
    )
    response = openai.ChatCompletion.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )

    return response