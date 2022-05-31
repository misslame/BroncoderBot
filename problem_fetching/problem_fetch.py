import requests
from html2image import Html2Image

endpoint = "https://leetcode.com/graphql"

EASY_DIFFICULTY = "EASY"
MEDIUM_DIFFICULTY = "MEDIUM"
HARD_DIFFICULTY = "HARD"
RANDOM_DIFFICLUTY= "RANDOM"

# add async later
async def getRandomQuestion(difficulty=RANDOM_DIFFICLUTY, skip_paid = True):
    query = """
    query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) 
    {
        randomQuestion(categorySlug: $categorySlug, filters: $filters) {
            categoryTitle
            questionId
            difficulty
            isPaidOnly
            titleSlug
            title
            translatedTitle
            codeDefinition
            content
            translatedContent
            difficulty
            likes
            dislikes
            similarQuestions
            topicTags {
                name
            }
            codeSnippets {
                lang
                langSlug
                code
                __typename
            }
            stats
            hints
            exampleTestcases
            sampleTestCase
            metaData
            enableRunCode
        }
    }
    """
    variables={
        "categorySlug": "Algorithms", 
        "filters": {

        }
    }
    if difficulty != RANDOM_DIFFICLUTY:
        variables["filters"]["difficulty"] = difficulty
    def get():
        res = requests.get(endpoint, json={'query': query , 'variables': variables}).json()
        if res["data"]["randomQuestion"]["isPaidOnly"] and skip_paid:
            print("got paid question, retrying...")
            res = get()
        return res
    
    # print(res.json()["data"]["randomQuestion"]["titleSlug"])
    return get()["data"]["randomQuestion"]

# def getProblemImage(content):
#     hti.screenshot(html_str=content,css_str = "body {background: white;font-family: Arial;}", save_as='test.jpg', size=(1920,1080))
    
