import torch
import numpy as np
import string
import random
import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from generator.serializer import nameGenSerializer


max_length = 20
all_categories = ['Arabic', 'Chinese', 'Czech', 'Dutch', 'English', 'French', 'German', 'Greek', 'Irish', 'Italian', 'Japanese', 'Korean', 'Polish', 'Portuguese', 'Russian', 'Scottish', 'Spanish', 'Vietnamese']
n_categories = len(all_categories)
all_letters = string.ascii_letters + " .,;'-"
n_letters = len(all_letters) + 1


# One-hot vector for category
def categoryTensor(category):
    li = all_categories.index(category)
    tensor = torch.zeros(1, n_categories)
    tensor[0][li] = 1
    return tensor

# One-hot matrix of first to last letters (not including EOS) for input
def inputTensor(line):
    tensor = torch.zeros(len(line), 1, n_letters)
    for li in range(len(line)):
        letter = line[li]
        tensor[li][0][all_letters.find(letter)] = 1
    return tensor

# LongTensor of second letter to end (EOS) for target
def targetTensor(line):
    letter_indexes = [all_letters.find(line[li]) for li in range(1, len(line))]
    letter_indexes.append(n_letters - 1) # EOS
    return torch.LongTensor(letter_indexes)

# Sample from a category and starting letter
def sample(category, start_letter='A'):
    with torch.no_grad():  # no need to track history in sampling
        category_tensor = categoryTensor(category)
        input = inputTensor(start_letter)
        hidden = the_model.initHidden()

        output_name = start_letter

        for i in range(max_length):
            output, hidden = the_model(category_tensor, input[0], hidden)
            topv, topi = output.topk(4)
            positive = [item + abs(topv[0][-1]) for item in topv[0]]
            sum_items = sum(positive)
            percentage = np.array([item/sum_items for item in positive])
            topi = np.random.choice(topi[0],p=percentage.ravel())
            if topi == n_letters - 1:
                break
            else:
                letter = all_letters[topi]
                output_name += letter
            input = inputTensor(letter)

        return output_name

# Get multiple samples from one category and multiple starting letters
def samples(category, start_letters='ABC'):
    for start_letter in start_letters:
        return sample(category, start_letter)


the_model = torch.load("model.pkl")


class genName(APIView):

    def get(self, request):
        try:
            language = request.GET["lang"]
            language = language.title()
        except:
            res = {"code": 400, "message": "No language specified."}
            return Response(data=json.dumps(res), status=status.HTTP_404_NOT_FOUND)
        if language not in all_categories:
            res = {"code": 400, "message": "Not able to use this language."}
            return Response(data=json.dumps(res), status=status.HTTP_404_NOT_FOUND)

        name = samples(language, random.choice(string.ascii_letters).upper())
        name_gen = nameGenSerializer(data={"language":language, "name": name})
        name_gen.is_valid()
        return Response(name_gen.data)


class GetLanguages(APIView):

    def get(self, request):
        return Response(data=all_categories, status=status.HTTP_200_OK)