import time
import logging
import os
import re
from tqdm import trange
import json
from langchain_core.prompts import PromptTemplate
from groq import Groq
import pandas as pd
import asyncio


## load env variables
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
CHAT_MODEL = "llama3-70b-8192"
client = Groq()

GENERATE_BAD_HUMAN_ANSWERS = """You are an expert in linguistic variation and medical communication. 
Take it that the answer provided is a 10/10 answer. 
Your task is to generate 5 poor answers that would be of a 3/10 quality for a given question-answer pair. 

Given Question:
{qn}
Given Answer:
{ans}

The returning format should be like this:
{{"3/10": [
            "poor answer 1",
            "poor answer 2",
            "poor answer 3",
            "poor answer 4",
            "poor answer 5"
        ]
}}

Unacceptable answer format:
Here are five answers that meet the quality requirement:
1. In what setting do the majority of cardiac arrests occur, according to a study conducted in Singapore in 2019?
answer: The majority of cardiac arrests occur in the hospital, with 26 of cases occurring in this setting, according to a study conducted in Singapore in 2019.
2. What is the most common cause of cardiac arrests, according to a study conducted in Singapore in 2019?
answer: The most common cause of cardiac arrests is coronary artery disease, with 42 of cases being attributed to this cause, according to a study conducted in Singapore in 2019.

Ensure and double check that the answer follows the format above strictly.
"""


GENERATE_SATISFACTORY_HUMAN_ANSWERS = """You are an expert in linguistic variation and medical communication. 
Take it that the answer provided is a 10/10 answer. 
Your task is to generate 5 satisfactory answers that would be of a 6/10 quality for a given question-answer pair. 

Given Question:
{qn}
Given Answer:
{ans}

The returning format should be like this:
{{"6/10": [
            "satisfactory answer 1",
            "satisfactory answer 2",
            "satisfactory answer 3",
            "satisfactory answer 4",
            "satisfactory answer 5"
        ]
}}
Unacceptable answer format:
Here are five answers that meet the quality requirement:
1. In what setting do the majority of cardiac arrests occur, according to a study conducted in Singapore in 2019?
answer: The majority of cardiac arrests occur in the hospital, with 26 of cases occurring in this setting, according to a study conducted in Singapore in 2019.
2. What is the most common cause of cardiac arrests, according to a study conducted in Singapore in 2019?
answer: The most common cause of cardiac arrests is coronary artery disease, with 42 of cases being attributed to this cause, according to a study conducted in Singapore in 2019.

Ensure and double check that the answer follows the format above strictly.
"""

GENERATE_GOOD_HUMAN_ANSWERS = """You are an expert in linguistic variation and medical communication. 
Take it that the answer provided is a 10/10 answer. 
Your task is to generate 5 good answers that would be of a 8.5/10 quality for a given question-answer pair. 

Given Question:
{qn}
Given Answer:
{ans}

The returning format should be like this:
{{"8.5/10": [
            "good answer 1",
            "good answer 2",
            "good answer 3",
            "good answer 4",
            "good answer 5"
        ]
}}

Unacceptable answer format:
Here are five answers that meet the quality requirement:
1. In what setting do the majority of cardiac arrests occur, according to a study conducted in Singapore in 2019?
answer: The majority of cardiac arrests occur in the hospital, with 26 of cases occurring in this setting, according to a study conducted in Singapore in 2019.
2. What is the most common cause of cardiac arrests, according to a study conducted in Singapore in 2019?
answer: The most common cause of cardiac arrests is coronary artery disease, with 42 of cases being attributed to this cause, according to a study conducted in Singapore in 2019.

Ensure and double check that the answer follows the format above strictly.
"""


def extract_poor_answer(input_string):
    # Find the start and end indices of the JSON data within the input string
    # Assuming the JSON data starts with '{' and ends with '}'
    json_start = input_string.find("{")
    json_end = input_string.rfind("}") + 1

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
        pattern = r'{"3/10":\s*\[.*?\]}'
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            # If a match is found, extract the matched JSON string and convert it to a dictionary
            data_json_str = match.group(0)
            data_dict = json.loads(data_json_str)
            return data_dict

        # If no valid JSON is found, the function will Log an error
        else:
            print(input_string)
            logging.error(
                "No dictionary with '3/10' as a key found in this input string. Error by LLM"
            )
            return {"error": "No dictionary with '3/10' found"}


def generate_poor_answers(question, answer, client):
    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=GENERATE_BAD_HUMAN_ANSWERS,
        input_variables=["query", "document"],
    )

    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(qn=question, ans=answer)

    # Generate the completion by interacting with the language model API
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0,  # Control the randomness of the output (lower means less random)
        max_tokens=1024,  # Limit the response length
        top_p=1,  # Nucleus sampling parameter (1 means only the most likely tokens are considered)
        stream=True,  # Enable streaming of the response chunks
        stop=None,  # Define stopping conditions (None means no stopping condition)
    )

    # Initialize an empty string to accumulate the response content
    answer = """"""
    for chunk in completion:
        # Append each chunk of content to the answer string
        answer += chunk.choices[0].delta.content or ""
    cleaned_answer = extract_poor_answer(answer)
    # Return the dictionary containing the generated answers
    return cleaned_answer


def extract_satisfactory_answer(input_string):
    # Find the start and end indices of the JSON data within the input string
    # Assuming the JSON data starts with '{' and ends with '}'
    json_start = input_string.find("{")
    json_end = input_string.rfind("}") + 1

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
        pattern = r'{"6/10":\s*\[.*?\]}'
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            # If a match is found, extract the matched JSON string and convert it to a dictionary
            data_json_str = match.group(0)
            data_dict = json.loads(data_json_str)
            return data_dict

        # If no valid JSON is found, the function will Log an error
        else:
            print(input_string)
            logging.error(
                "No dictionary with '6/10' as a key found in this input string. Error by LLM"
            )
            return {"error": "No dictionary with '6/10' found"}


def generate_satisfactory_answers(question, answer, client):
    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=GENERATE_SATISFACTORY_HUMAN_ANSWERS,
        input_variables=["query", "document"],
    )

    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(qn=question, ans=answer)

    # Generate the completion by interacting with the language model API
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0,  # Control the randomness of the output (lower means less random)
        max_tokens=1024,  # Limit the response length
        top_p=1,  # Nucleus sampling parameter (1 means only the most likely tokens are considered)
        stream=True,  # Enable streaming of the response chunks
        stop=None,  # Define stopping conditions (None means no stopping condition)
    )

    # Initialize an empty string to accumulate the response content
    answer = """"""
    for chunk in completion:
        # Append each chunk of content to the answer string
        answer += chunk.choices[0].delta.content or ""
    cleaned_answer = extract_satisfactory_answer(answer)
    # Return the dictionary containing the generated answers
    return cleaned_answer


def extract_good_answer(input_string):
    # Find the start and end indices of the JSON data within the input string
    # Assuming the JSON data starts with '{' and ends with '}'
    json_start = input_string.find("{")
    json_end = input_string.rfind("}") + 1

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
        pattern = r'{"8.5/10":\s*\[.*?\]}'
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            # If a match is found, extract the matched JSON string and convert it to a dictionary
            data_json_str = match.group(0)
            data_dict = json.loads(data_json_str)
            return data_dict

        # If no valid JSON is found, the function will Log an error
        else:
            print(input_string)
            logging.error(
                "No dictionary with '8.5/10' as a key found in this input string. Error by LLM"
            )
            return {"error": "No dictionary with '8.5/10' found"}


def generate_good_answers(question, answer, client):
    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=GENERATE_GOOD_HUMAN_ANSWERS,
        input_variables=["query", "document"],
    )

    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(qn=question, ans=answer)

    # Generate the completion by interacting with the language model API
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0,  # Control the randomness of the output (lower means less random)
        max_tokens=1024,  # Limit the response length
        top_p=1,  # Nucleus sampling parameter (1 means only the most likely tokens are considered)
        stream=True,  # Enable streaming of the response chunks
        stop=None,  # Define stopping conditions (None means no stopping condition)
    )

    # Initialize an empty string to accumulate the response content
    answer = """"""
    for chunk in completion:
        # Append each chunk of content to the answer string
        answer += chunk.choices[0].delta.content or ""
    cleaned_answer = extract_good_answer(answer)
    # Return the dictionary containing the generated answers
    return cleaned_answer


def main():
    with open(
        "../data/synthetically_generated_qa_pairs.json", "r", encoding="utf-8"
    ) as fin:
        pairs = json.load(fin)

    new_data = []
    for i in trange(14, len(pairs)):
        question = pairs[i]["Question"]
        answer = pairs[i]["Answer"]
        data = {}
        data["QA_pair_number"] = i
        data["Question"] = question
        data["Answer"] = answer
        try:
            poor_answer = generate_poor_answers(question, answer, client)
        except ValueError:
            for _ in range(2):
                poor_answer = generate_poor_answers(question, answer, client)
            if poor_answer:
                break
        time.sleep(1)
        try:
            satisfactory_answer = generate_satisfactory_answers(
                question, answer, client
            )
        except ValueError:
            for _ in range(2):
                satisfactory_answer = generate_satisfactory_answers(
                    question, answer, client
                )
                if satisfactory_answer:
                    break
        time.sleep(1)
        try:
            good_answer = generate_good_answers(question, answer, client)
        except ValueError:
            for _ in range(2):
                good_answer = generate_good_answers(question, answer, client)
                if good_answer:
                    break

        data["3/10"] = poor_answer.get("3/10")
        data["6/10"] = satisfactory_answer.get("6/10")
        data["8.5/10"] = good_answer.get("8.5/10")

        new_data.append(data)
        with open(
            "../data/further_prompting/QA_pairs_with_answer_range(14-).json",
            "w",
            encoding="utf-8",
        ) as fout:
            json.dump(new_data, fout, ensure_ascii=False, indent=4)

        if i > 3 and i % 3 == 0:
            print("Sleeping now...")
            time.sleep(30)


if __name__ == "__main__":
    main()
