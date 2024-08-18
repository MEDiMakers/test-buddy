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


GENERATE_QUESTION_PROMPT = \
'''You are a professor with deep expertise in medical aid, particularly in the context of hospital nursing practices. 
You have been tasked with creating high-quality test questions for an upcoming examination based on the content of a medical information manual used by hospital nurses in Singapore.

Your objective is to generate 5 test questions that accurately assess the understanding and application of the information contained within the text corpus provided below.
Ensure that the questions are challenging, relevant, and designed to test the critical knowledge and skills that hospital nurses need to perform effectively.
The questions should focus on key concepts, procedures, and practical scenarios that nurses are likely to encounter in their professional duties.
Do not mention "according to the text corpus" in the question.

Text Corpus:
{text}

Do not provide the answers.
{format_instructions}
Ensure and double check that the answer is in accordance to the format above.
'''


GENERATE_ANSWER_PROMPT = \
'''You are a professor proficient in medical aid with extensive experience in hospital nursing practices. 
You have been tasked with generating answers for a test based on the content of a medical information manual used by hospital nurses in Singapore.

Your goal is to produce answers that not only reference the text corpus provided below but also reflect the depth of understanding, critical thinking, and practical application that a seasoned nurse or medical professional would demonstrate.
Ensure that each answer is thorough, well-elaborated, and aligns with how an experienced human would logically and intuitively respond to the questions.
I do not want one worded answers. 
Do not mention the word "according to the text corpus" in the answer.

Text Corpus:
{text}

List of questions:
{question_list}
{format_instructions}

Ensure and double check that the answer is in accordance to the format above.
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


def generate_questions(page_text, question_prompt, client):
    """
    Generates questions from a given text corpus using a language model.

    This function takes in a text corpus and a question prompt template, then utilizes a
    language model to generate questions based on the content of the text. The generated
    questions are returned as a dictionary.

    Args:
        page_text (str): The text corpus from which questions will be generated.
        question_prompt (str): A template prompt used to instruct the model on how to generate questions.
        client: A client object for interacting with the language model API.

    Returns:
        dict: A dictionary containing the generated questions.

    Raises:
        KeyError: If the 'error' key is found in the response dictionary.
    """

    # Define a Pydantic model for the expected question structure
    class Questions(BaseModel):
        questions: str = Field(description="Question about the content in the text corpus")
    
    # Initialize a JSON output parser using the defined Pydantic model
    parser = JsonOutputParser(pydantic_object=Questions)

    # Prepare the prompt using the provided question prompt template and input text
    prompt = PromptTemplate(
        template=question_prompt,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    ) 
    
    # Format the final prompt with the actual text data
    final_prompt = prompt.format(text=page_text)

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
    
    # Extract the questions from the accumulated response content
    question_dict = extract_answer(answer)

    # Log an error if the response contains an 'error' key
    if "error" in question_dict:
        logging.error(f"{question_dict['error']}")
    
    # Return the dictionary containing the generated questions
    return question_dict
    
    
def generate_answers(page_text, questions, answer_prompt, client):
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

    # Define a Pydantic model for the expected answer structure
    class AnswerList(BaseModel):
        answers: list = Field(description="Answer to the question with reference to the content in the text corpus")
    
    # Initialize a JSON output parser using the defined Pydantic model
    parser = JsonOutputParser(pydantic_object=AnswerList)

    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=answer_prompt,
        input_variables=["text", "question_list"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    ) 
    
    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(text=page_text, question_list=questions)

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


def generate_section_QA_pairs(section_text, client, question_prompt, answer_prompt):
    """
    Generates question-answer (QA) pairs from a given section of text using a language model.

    This function first generates questions based on the input section of text, then uses the
    generated questions to produce corresponding answers. The questions and answers are paired
    together and returned as a list of dictionaries.

    Args:
        section_text (str): The text from which questions and answers will be generated.
        client: A client object for interacting with the language model API.
        question_prompt (str): A template prompt used to instruct the model on how to generate questions.
        answer_prompt (str): A template prompt used to instruct the model on how to generate answers.

    Returns:
        list: A list of dictionaries, each containing a question and its corresponding answer.
    """

    # Generate questions from the provided text section using the question prompt
    question_dict = generate_questions(section_text, question_prompt, client)
    print(question_dict)
    # Extract the list of questions from the generated question dictionary
    if 'error' in question_dict:
        question_dict = generate_questions(section_text, question_prompt, client)
        
    question_list = [q_pair for q_pair in question_dict['questions']]
        
    # Convert the list of questions to a JSON-formatted string
    question_str = json.dumps(question_list)

    # Generate answers corresponding to the questions using the answer prompt
    answer_dict = generate_answers(section_text, question_str, answer_prompt, client)

    # Extract the list of answers from the generated answer dictionary
    answer_list = answer_dict["answers"]

    # Extract the list of questions again for pairing with answers
    question_list = question_dict['questions']

    # Initialize an empty list to store the QA pairs
    qa_pairs = []
    
    # Pair each question with its corresponding answer and append to the QA pairs list
    for i in range(len(question_list)):
        qa_pairs.append({"Question": question_list[i], "Answer": answer_list[i]})
    
    # Return the list of question-answer pairs
    return qa_pairs


def generate_all_qa_pairs():
    """
    Generates QA pairs for all sections of text stored in a JSON file and saves them to a new file.

    This function reads sections of text from a JSON file, generates QA pairs for each section
    using the `generate_section_QA_pairs` function, and writes the resulting QA pairs to another
    JSON file. The function also includes rate limiting to comply with API usage limits.

    Returns:
        None
    """     
    
    # Open and load the text data from the specified JSON file
    with open("../data/all_pdf_text.json", "r", encoding="utf-8") as fin:
        all_sections = json.load(fin)
    
    # Initialize an empty list to store all QA pairs
    all_pairs = []

    # Iterate over each section of text to generate QA pairs
    for i in trange(len(all_sections)):
        # Generate QA pairs for the current section
        section_qa_pair = generate_section_QA_pairs(all_sections[i], client, GENERATE_QUESTION_PROMPT, GENERATE_ANSWER_PROMPT)
        
        # Extend the list of all QA pairs with the newly generated pairs
        all_pairs.extend(section_qa_pair)
        
        # Write the QA pairs to a JSON file after each iteration to avoid data loss
        with open("../data/2_Draft_QA_pairs_generated.json", "w", encoding='utf-8') as fout:
            json.dump(all_pairs, fout, ensure_ascii=False, indent=4)
            
        # Implement a delay after every 30 sections to avoid exceeding the API rate limit
        if i > 10 and i % 11 == 0:
            print("limit reached.. sleeping now...\n")
            time.sleep(62)

if __name__ == "__main__":
    generate_all_qa_pairs()

