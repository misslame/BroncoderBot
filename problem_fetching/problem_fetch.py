import requests

endpoint = "https://leetcode.com/graphql"

# add async later
def getRandomQuestion():
    query = """
    query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) {
        randomQuestion(categorySlug: $categorySlug, filters: $filters) {
            titleSlug
            questionId
            title
            translatedTitle
            codeDefinition
            content
            translatedContent
            difficulty
            likes
            dislikes
            similarQuestions
            submitUrl
            topicTags {
                name
                slug
                translatedName
                __typename
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
        "categorySlug": "", 
        "filters": {
            "difficulty": "MEDIUM"
        }
    }
    res = requests.get(endpoint, json={'query': query , 'variables': variables})
    # print(res.json()["data"]["randomQuestion"]["titleSlug"])
    print(res.json())

getRandomQuestion()