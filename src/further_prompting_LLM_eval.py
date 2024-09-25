import os
import json
import re

from langchain_core.prompts import PromptTemplate
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
CHAT_MODEL = "llama3-70b-8192"
client = Groq()


PROMPT = """You are an expert in linguistic variation and medical communication. 
You are provided with a medical question, a persons answer to that question, and the model answer to that question. 
Your task is to generate a follow up question that aids the user in the answering of the question. 
You are to focus in on what is missing from the users answer in comparison to the model answer, and hint that to the user in the follow up question.
You are to reply in a cheerful, friendly tone.

Question:
{question}

Users Answer:
{user_ans}

Model answer:
{model_ans}

The returning format should be like this:
{{"guiding_question": "Question to help the user better answer the question"}}

Before returning the answer, ensure and double check that the answer is in accordance to the format above.
"""


def load_data(index):
    with open(
        "../data/further_prompting/combined_data.json", "r", encoding="utf-8"
    ) as fin:
        data = json.load(fin)
    return data[index]


def extract_answer(answer, pattern=r'"guiding_question"\s*:\s*"([^"]+)"'):
    """
    Extracts the answer from the text associated with the key "guiding_question".

    """
    try:
        # Search for the pattern in the input text
        match = re.search(pattern, answer)

        # If a match is found, return the captured group (the question)
        if match:
            return match.group(1)
        else:
            # If no match is found, return an error message
            return "No guiding question found in the input text."

    except Exception as e:
        # If any unexpected error occurs, return a generic error message
        return f"An error occurred: {str(e)}"


def generate_guiding_question(qn, user_ans, model_ans) -> str:
    """Generates the question used to re-prompt the user,
    helping him to answer the question better with some hints"""

    prompt = PromptTemplate(
        template=PROMPT, input_variables=["question", "user_ans", "model_ans"]
    )

    final_prompt = prompt.format(question=qn, user_ans=user_ans, model_ans=model_ans)

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    llm_answer = """"""
    for chunk in completion:
        llm_answer += chunk.choices[0].delta.content or ""

    # Improve error handling here
    guiding_qn = extract_answer(llm_answer)
    print("===================================")
    print(f"Question:\n{qn}\n")
    print("===================================")
    print(f"User's Answer:\n{user_ans}\n")
    print("===================================")
    print(f"Model Answer:\n{model_ans}\n")
    print("===================================")
    print(f"Guiding Question:\n{guiding_qn}\n")
    print("===================================")
    return guiding_qn


# TODO for Ethan (Generate answer similarity pipeline)
def get_answer_similarity(retry_ans, model_ans) -> float:
    """
    Takes in the users retried answer and the model answer.
    Uses finetuned cross encoder to generate similarity score
    """
    score = None
    return score


def main():
    data = load_data(4)
    model_ans = data["Answer"]
    qn = data["Question"]
    ans_index = 2
    user_ans = data["3/10"][ans_index]
    guiding_qn = generate_guiding_question(qn, user_ans, model_ans)


if __name__ == "__main__":
    main()
