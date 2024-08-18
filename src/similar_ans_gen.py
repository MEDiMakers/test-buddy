import pandas as pd
import os
import json
from tqdm import trange
import time
import re

from llama_index.legacy import Document
from llama_index.legacy.schema import TextNode
from llama_index.legacy.node_parser import SentenceWindowNodeParser, SemanticSplitterNodeParser
from llama_index.legacy.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.legacy.finetuning import (
    generate_qa_embedding_pairs,
    EmbeddingQAFinetuneDataset,
) 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from groq import Groq

## load evv variables
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY       = os.environ["GROQ_API_KEY"]
CHAT_MODEL         = "llama3-70b-8192"
client = Groq()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GENERATE_SIMILAR_ANSWER_PROMPT = \
'''You are an expert in linguistic variation and medical communication. 
Your task is to generate 5 similar, yet distinct, answers for a given question-answer pair. 
These answers should maintain the core meaning and accuracy of the original answer but vary in phrasing, word choice, and sentence structure to provide different ways of expressing the same response. 
The variations should be natural, contextually appropriate, and reflect the kind of nuanced responses that different knowledgeable individuals might provide.

For each question-answer pair provided below, generate 5 alternative answers that are consistent with the original answer's intent and content:

Question:
{question}

Original Answer:
{answer}
{format_instructions}

Ensure and double check that the answer is in accordance to the format above.
'''

GENERATE_POOR_ANSWER_PROMPT = \
'''You are an expert in generating misleading and irrelevant content. 
Your task is to produce 5 responses for a given question-answer pair that are completely opposite, incorrect, and irrelevant to the original answer.
These responses should disregard the core meaning and accuracy of the original answer, instead focusing on providing misleading, confusing, or nonsensical information.
The variations should be inconsistent, contextually inappropriate, and reflect the kind of responses that lack knowledge or understanding.

For each question-answer pair provided below, generate 5 alternative answers that are contradictory, poorly constructed, and irrelevant to the original answer's intent and content:

Question:
{question}

Original Answer:
{answer}
{format_instructions}

Ensure and double-check that the generated answers are incoherent, misleading, and do not align with the original answer in any meaningful way.
'''

def extract_answer(input_string):
    """
    Extracts and returns the JSON data from a given input string.

    This function attempts to extract a JSON object from the provided input string.
    The input string is expected to contain JSON data starting with `{` and ending
    with `}`. If a valid JSON object is not found, it attempts to locate a JSON object
    containing a 'questions' key using regular expressions.

    Args:
        input_string (str): The input string that potentially contains JSON data.

    Returns:
        dict: A dictionary representing the extracted JSON data.

    Raises:
        ValueError: If no JSON data is found in the input string.
        json.JSONDecodeError: If the JSON data is malformed and cannot be parsed.

    """
    # Find the start and end indices of the JSON data within the input string
    # Assuming the JSON data starts with '{' and ends with '}'
    json_start = input_string.find('{')
    json_end = input_string.rfind('}') + 1
    
    # If either the start or end index is not found, raise an error
    if json_start == -1 or json_end == -1:
        raise ValueError("Invalid input: No JSON data found.")

    # Extract the substring that potentially contains the JSON data
    json_data = input_string[json_start:json_end]
    
    try:
        # Attempt to convert the JSON string to a Python dictionary
        data_dict = json.loads(json_data)
        return data_dict
    
    except json.JSONDecodeError:
        # If JSON decoding fails, search for a JSON object containing the 'questions' key
        # Using regex to match a pattern that includes the 'questions' key
        pattern = r'{\s*"questions":\s*\[.*?\]\s*}'
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            # If a match is found, extract the matched JSON string and convert it to a dictionary
            data_json_str = match.group(0)
            data_dict = json.loads(data_json_str)
            return data_dict

        # If no valid JSON is found, the function will Log an error
        else:
            logging.error("No dictionary with 'questions' as a key found in this input string. Error by LLM")
            return {"error": "No dictionary with questions found"}

def generate_answers(qa_pair, answer_prompt, client):
    """
    Generates answers based on a list of questions and a text corpus using a language model.

    This function takes in a text corpus and a list of questions, and uses a language model
    to generate corresponding answers. The answers are formatted according to the provided
    prompt template and are returned as a dictionary.

    Args:
        page_text (str): The text corpus from which answers will be generated.
        questions (str): A list of questions in json string that the model should answer based on the text.
        answer_prompt (str): A template prompt used to instruct the model on how to generate answers.
        client: A client object for interacting with the language model API.

    Returns:
        dict: A dictionary containing the generated answers.

    Raises:
        KeyError: If the 'error' key is found in the response dictionary.
    """
    
    qn = qa_pair['Question']
    ans = qa_pair['Answer']

    # Define a Pydantic model for the expected answer structure
    class AnswerList(BaseModel):
        answers: list = Field(description="Similar answer to the provided answer")
    
    # Initialize a JSON output parser using the defined Pydantic model
    parser = JsonOutputParser(pydantic_object=AnswerList)

    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=answer_prompt,
        input_variables=["answer", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    ) 
    
    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(question=qn, answer=ans)

    # Generate the completion by interacting with the language model API
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        temperature=0,  # Control the randomness of the output (lower means less random)
        max_tokens=1024,  # Limit the response length
        top_p=1,  # Nucleus sampling parameter (1 means only the most likely tokens are considered)
        stream=True,  # Enable streaming of the response chunks
        stop=None,  # Define stopping conditions (None means no stopping condition)
    )

    # Initialize an empty string to accumulate the response content
    answer = ''''''
    for chunk in completion:
        # Append each chunk of content to the answer string
        answer += chunk.choices[0].delta.content or ""
    
    # Extract the answers from the accumulated response content
    answer_dict = extract_answer(answer)

    # Log an error if the response contains an 'error' key
    if "error" in answer_dict:
        logging.error(f"{answer_dict['error']}")
    
    # Return the dictionary containing the generated answers
    return answer_dict


if __name__ == "__main__":
    with open("../data/final_draft_2_pairs.json", "r", encoding="utf-8") as fin:
        pairs = json.load(fin)    

    output_file = "../data/updated_pairs.json"
    
    all_data = []

    for i in trange(len(pairs)):
        dic = {}
        dic['index'] = i
        
        sim_ans  = generate_answers(pairs[i], GENERATE_SIMILAR_ANSWER_PROMPT, client)
        poor_ans = generate_answers(pairs[i], GENERATE_POOR_ANSWER_PROMPT, client)

        dic['Similar Answers'] = sim_ans['answers']
        dic['Poor Answers'] = poor_ans['answers']

        all_data.append(dic)

        # Write the entire list to the JSON file after each iteration
        with open(output_file, "w", encoding="utf-8") as fout:
            json.dump(all_data, fout, ensure_ascii=False, indent=4)

        # account for rate limit
        if i > 0 and i % 5 == 0:
            time.sleep(62)
            print("Sleeping now...")