from langchain_community.document_loaders import JSONLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import HuggingFaceDatasetLoader

from utils.FuncUtils import getFunctionName
from utils.PreprocessUtils import removeMetaData
import re


def connectDB(
    dataset_name="openai_humaneval", page_content_column="canonical_solution"
):
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    loader = HuggingFaceDatasetLoader(dataset_name, page_content_column)
    data = loader.load()
    db = Chroma.from_documents(data, embedding_function)
    return db

def getOneShot(db, code):
    query = code
    docs = db.similarity_search(query)
    test_cases_of_few_shot = docs[0].metadata["test"]
    description_of_few_shot = docs[0].metadata["prompt"]

    return test_cases_of_few_shot


def getFewShots(db, code):
    test_cases_of_few_shotList = []
    description_of_few_shotList = []
    code_of_few_shotList = []
    query = code
    docs = db.similarity_search(query)
    # adjust the range to specify number of few shot examples
    for i in range(0, 4):

        test_cases_of_few_shot = docs[i].metadata["test"]
        description_of_few_shot = docs[i].metadata["prompt"]
        code_of_few_shot = docs[i].page_content
        # remove quotation mark from begeinning of code
        indexer = 0
        if code_of_few_shot[0] == '"':
            indexer += 1
        # remove spaces from 1st line of code
        while code_of_few_shot[indexer] == " ":
            indexer += 1
        code_of_few_shot = code_of_few_shot[indexer:]
        # remove quotation mark from end of code
        if code_of_few_shot[len(code_of_few_shot) - 1] == '"':
            code_of_few_shot = code_of_few_shot[: len(code_of_few_shot) - 1]
        # get the function header
        description_of_few_shot, utility = getFunctionName(description_of_few_shot)
        code_of_few_shot = re.sub(r"\\n", "\n", code_of_few_shot)
        # print(test_cases_of_few_shot)
        code_of_few_shot = utility + "\n" + description_of_few_shot + code_of_few_shot
        test_cases_of_few_shotList.append(test_cases_of_few_shot)
        description_of_few_shotList.append(description_of_few_shot)
        code_of_few_shotList.append(code_of_few_shot)

    test_cases_of_few_shot = removeMetaData(test_cases_of_few_shotList)
    return (code_of_few_shotList, test_cases_of_few_shotList)
