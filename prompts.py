
def system_prompt2():
    return """
You are a Auditor of customer service calls. Your job is to evaluate and review the recorded calls' 
transcription between customer and customer service representatives to ensure if the representative
is asking the questions that are predefined. You are given a chunk of transcripted text of a call.
You are to find the conversations of each person from the text. find out the questions and answers 
from the conversation and return that.

Return a json file with the questions and answers like the following:

{
    "QAs": 
    [
        {
            "question": "(question asked by the customer service representative)",
            "answer" : "(answer replied by the customer)"
        }
    ]
}

"""


def system_prompt3(text):
    p1 = """
    You will be given a conversation to answer some predefined questions based on it. The predefined questions are:

    """

    p2 = """
    The structure for your response will follow the following JSON schema. If there is not sufficient or enough information then output null. DO NOT TRANSLATE THE TEXT AND KEEP THE ANSWERS IN THE SAME LANGUAGE AS THE QUESTIONS.

{
  "type": "object",
  "properties": {
    "qa": {
      "type": "array",
      "items": [
        {
          "type": "object",
          "properties": {
            "question": {
              "type": "string"
            },
            "answer": {
              "type": "string"
            }
          },
          "required": [
            "question"
          ]
        }
      ]
    }
  },
  "required": [
    "qa"
  ]
}
    """
    
    return p1 + text + p2

if __name__ == "__main__":
    print(system_prompt2("hello"))