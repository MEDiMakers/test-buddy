from audio.groq_hear import Hear
from llm.llm import LLM


def main(API_KEY, query):
    llm = LLM()
    audio = Hear()

    transcription = audio.start(API_KEY = API_KEY)
    llm.get_score(query, transcription)


if __name__ == "__main__":
    x = input("Input your API")
    y = input("Doctor: Input the desired question")
    main(x,y)


