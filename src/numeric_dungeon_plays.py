
class DecisionNo:
    pass

class DecisionYes:
    pass

class Answer:
    def __init__(self, answer):
        self.answer = answer

class Question:
    def __init__(self, question):
        self.question = question

class Activate:
    def __init__(self, indexes):
        self.indexes = indexes