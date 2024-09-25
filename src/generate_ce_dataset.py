from dataclasses import dataclass
import time
import logging
import os
from tqdm import trange
import json
from langchain_core.prompts import PromptTemplate
from groq import Groq
import pandas as pd


## load env variables
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
CHAT_MODEL = "llama3-70b-8192"
client = Groq()

DEFAULT_QUERY_DOC_RELEVANCE_PROMPT = '''You are an Assistant responsible for helping detect whether the retrieved document is relevant to the query. For a given input, you need to output a single token: "Yes" or "No" indicating the retrieved document is relevant to the query.

Query: How to plant a tree?
Document: """Cars were invented in 1886, when German inventor Carl Benz patented his Benz Patent-Motorwagen.[3][4][5] Cars became widely available during the 20th century. One of the first cars affordable by the masses was the 1908 Model T, an American car manufactured by the Ford Motor Company. Cars were rapidly adopted in the US, where they replaced horse-drawn carriages.[6] In Europe and other parts of the world, demand for automobiles did not increase until after World War II.[7] The car is considered an essential part of the developed economy."""
Relevant: No

Query: Has the coronavirus vaccine been approved?
Document: """The Pfizer-BioNTech COVID-19 vaccine was approved for emergency use in the United States on December 11, 2020."""
Relevant: Yes

Query: What is the capital of France?
Document: """Paris, France's capital, is a major European city and a global center for art, fashion, gastronomy and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine. Beyond such landmarks as the Eiffel Tower and the 12th-century, Gothic Notre-Dame cathedral, the city is known for its cafe culture and designer boutiques along the Rue du Faubourg Saint-Honoré."""
Relevant: Yes

Query: What are some papers to learn about PPO reinforcement learning?
Document: """Proximal Policy Optimization and its Dynamic Version for Sequence Generation: In sequence generation task, many works use policy gradient for model optimization to tackle the intractable backpropagation issue when maximizing the non-differentiable evaluation metrics or fooling the discriminator in adversarial learning. In this paper, we replace policy gradient with proximal policy optimization (PPO), which is a proved more efficient reinforcement learning algorithm, and propose a dynamic approach for PPO (PPO-dynamic). We demonstrate the efficacy of PPO and PPO-dynamic on conditional sequence generation tasks including synthetic experiment and chit-chat chatbot. The results show that PPO and PPO-dynamic can beat policy gradient by stability and performance."""
Relevant: Yes

Query: Explain sentence embeddings
Document: """Inside the bubble: exploring the environments of reionisation-era Lyman-α emitting galaxies with JADES and FRESCO: We present a study of the environments of 16 Lyman-α emitting galaxies (LAEs) in the reionisation era (5.8<z<8) identified by JWST/NIRSpec as part of the JWST Advanced Deep Extragalactic Survey (JADES). Unless situated in sufficiently (re)ionised regions, Lyman-α emission from these galaxies would be strongly absorbed by neutral gas in the intergalactic medium (IGM). We conservatively estimate sizes of the ionised regions required to reconcile the relatively low Lyman-α velocity offsets (ΔvLyα<300kms−1) with moderately high Lyman-α escape fractions (fesc,Lyα>5%) observed in our sample of LAEs, indicating the presence of ionised ``bubbles'' with physical sizes of the order of 0.1pMpc≲Rion≲1pMpc in a patchy reionisation scenario where the bubbles are embedded in a fully neutral IGM. Around half of the LAEs in our sample are found to coincide with large-scale galaxy overdensities seen in FRESCO at z∼5.8-5.9 and z∼7.3, suggesting Lyman-α transmission is strongly enhanced in such overdense regions, and underlining the importance of LAEs as tracers of the first large-scale ionised bubbles. Considering only spectroscopically confirmed galaxies, we find our sample of UV-faint LAEs (MUV≳−20mag) and their direct neighbours are generally not able to produce the required ionised regions based on the Lyman-α transmission properties, suggesting lower-luminosity sources likely play an important role in carving out these bubbles. These observations demonstrate the combined power of JWST multi-object and slitless spectroscopy in acquiring a unique view of the early stages of Cosmic Reionisation via the most distant LAEs."""
Relevant: No

Query: {query}
Document: """{document}"""
Relevant:
'''


def generate_bool(context, question, relevance_prompt, client):
    # Prepare the prompt using the provided answer prompt template, text, and list of questions
    prompt = PromptTemplate(
        template=relevance_prompt,
        input_variables=["query", "document"],
    )

    # Format the final prompt with the actual text data and question list
    final_prompt = prompt.format(query=question, document=context)

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

    # Return the dictionary containing the generated answers
    return answer


@dataclass
class CrossEncoderFinetuningDatasetSample:
    """Class for keeping track of each item of Cross-Encoder training Dataset."""

    query: str
    context: str
    score: int


class InvalidResponseError(Exception):
    """Exception raised for invalid LLM output responses."""

    def __init__(self, response, message="Invalid LLM output. Edit prompt."):
        self.response = response
        self.message = message
        super().__init__(f"{message} Response: {response}")


# Adapted and modified from llama index open source library
def generate_ce_fine_tuning_dataset(
    contexts,
    clean_contexts,
    questions_list,
    qa_doc_relevance_prompt,
    client,
    output_file,
):

    k = 0
    for i in trange(len(questions_list)):
        for j in trange(len(contexts)):
            # Generates the Yes or No for each question document pair
            response = generate_bool(
                contexts[j], questions_list[i], qa_doc_relevance_prompt, client
            )
            # Lowercase the response
            result = response.lower()

            if result == "yes":
                question_row = {
                    "query": questions_list[i],
                    "context": clean_contexts[j],
                    "score": 1,
                }

            elif result == "no":
                question_row = {
                    "query": questions_list[i],
                    "context": clean_contexts[j],
                    "score": 0,
                }
            # Try again
            else:
                # Generates the Yes or No for each question document pair
                response = generate_bool(
                    contexts[j], questions_list[i], qa_doc_relevance_prompt, client
                )
                # Lowercase the response
                result = response.lower()
                if result == "yes":
                    question_row = {
                        "query": questions_list[i],
                        "context": clean_contexts[j],
                        "score": 1,
                    }

                elif result == "no":
                    question_row = {
                        "query": questions_list[i],
                        "context": clean_contexts[j],
                        "score": 0,
                    }
                else:
                    logging.error("Error in LLM output... Edit prompt")
                    print("-" * 100)
                    print(f"Index stopped at {i}")
                    print("-" * 100)
                    raise InvalidResponseError(result)

            # Convert the dictionary to a DataFrame and append it to the CSV file
            pd.DataFrame([question_row]).to_csv(
                output_file, mode="a", header=False, index=False
            )

            k += 1
            if k > 0 and k % 25 == 0:
                print("sleeping now..")
                time.sleep(60)

    return pd.read_csv(output_file)


if __name__ == "__main__":
    with open(
        "../data/combined_txts/combined_output.txt", "r", encoding="utf-8"
    ) as fin:
        contexts = fin.read()

    with open("../data/Final_QA_pairs.json", "r", encoding="utf-8") as fin:
        pairs = json.load(fin)

    sections = [section for section in contexts.split("\n\n\n") if section]
    clean_sections = [
        section.replace("\n", " ") for section in contexts.split("\n\n\n") if section
    ]
    questions = [pair["Question"] for pair in pairs]

    dataset_ls = generate_ce_fine_tuning_dataset(
        sections,
        clean_sections,
        questions[68:],
        DEFAULT_QUERY_DOC_RELEVANCE_PROMPT,
        client,
        output_file="../data/finetuning/ce_finetuning_dataset(68-80).csv",
    )
