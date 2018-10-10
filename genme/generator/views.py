import torch
import numpy as np
import string
import random
import json
import time
import unicodedata
import math

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from generator.serializer import *
from model import *
from generator.models import *

max_length = 20
# all_categories = ['Arabic', 'Chinese', 'Czech', 'Dutch', 'English', 'French', 'German', 'Greek', 'Irish', 'Italian', 'Japanese', 'Korean', 'Polish', 'Portuguese', 'Russian', 'Scottish', 'Spanish', 'Vietnamese']
# p2 = Categories(categories='names', id=1)
# p2.save()
splitter = ","
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
            topv, topi = output.topk(spread)
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


def train(category_tensor, input_line_tensor, target_line_tensor):
    criterion = nn.NLLLoss()
    learning_rate = 0.0005

    target_line_tensor.unsqueeze_(-1)
    hidden = rnn.initHidden()

    rnn.zero_grad()

    loss = 0

    for i in range(input_line_tensor.size(0)):
        output, hidden = rnn(category_tensor, input_line_tensor[i], hidden)
        l = criterion(output, target_line_tensor[i])
        loss += l

    loss.backward()

    for p in rnn.parameters():
        p.data.add_(-learning_rate, p.grad.data)

    return output, loss.item() / input_line_tensor.size(0)

# Random item from a list
def randomChoice(l):
    return l[random.randint(0, len(l) - 1)]

# Get a random category and random line from that category
def randomTrainingPair(category_lines):
    category = randomChoice(all_categories)
    line = randomChoice(category_lines[category])
    return category, line

# Make category, input, and target tensors from a random category, line pair
def randomTrainingExample(category_lines):
    category, line = randomTrainingPair(category_lines)
    category_tensor = categoryTensor(category)
    input_line_tensor = inputTensor(line)
    target_line_tensor = targetTensor(line)
    return category_tensor, input_line_tensor, target_line_tensor

# Turn a Unicode string to plain ASCII, thanks to http://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )

# Read a file and split into lines
def readLines(data_with_key):
    lines = data_with_key.strip().split(splitter)
    return [unicodeToAscii(line) for line in lines]


def timeSince(since):
    now = time.time()
    s = now - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)

# REAl view start here

class genName(APIView):

    def get(self, request):
        try:
            _spread = request.GET["spread"]
            global spread
            spread = int(_spread)
        except:
            res = {"code": 400, "message": "Please specify a spread. Spread increases randomness in the prediction."}
            return Response(data=json.dumps(res), status=status.HTTP_404_NOT_FOUND)
        # if language not in all_categories:
        #     res = {"code": 400, "message": "Not able to use this language."}
        #     return Response(data=json.dumps(res), status=status.HTTP_404_NOT_FOUND)
        global all_categories
        global n_categories

        category = Categories.objects.get(id=1).categories
        all_categories = []
        all_categories.append(category)
        n_categories = len(all_categories)
        name = samples(category, random.choice(string.ascii_letters).upper())
        name_gen = nameGenSerializer(data={"language":category, "name": name})
        name_gen.is_valid()
        return Response(name_gen.data)


class trainGenerator(APIView):

    def post(self, request):
        data = request.data["data"]
        category = request.data["category"]

        global all_categories
        global n_categories
        # Build the category_lines dictionary, a list of lines per category
        category_lines = {}
        all_categories = []
        all_categories.append(category)
        lines = readLines(data)
        category_lines[category] = lines
        n_categories = len(all_categories)

        global rnn
        rnn = RNN(n_letters, 128, n_letters, n_categories)

        n_iters = 100000
        print_every = 1000
        plot_every = 500
        all_losses = []
        total_loss = 0  # Reset every plot_every iters

        start = time.time()

        for iter in range(1, n_iters + 1):
            output, loss = train(*randomTrainingExample(category_lines))
            total_loss += loss

            if iter % print_every == 0:
                curr_status = '%s (%d %d%%) %.4f' % (timeSince(start), iter, iter / n_iters * 100, loss)
                print(curr_status)
                save_model = TrainingStatus(status=curr_status, id=1)
                save_model.save()

            if iter % plot_every == 0:
                all_losses.append(total_loss / plot_every)
                total_loss = 0
        torch.save(rnn, "model.pkl")
        cat = Categories(id=1, categories=category)
        cat.save()
        return Response(data={"successfully trained and saved model."}, status=status.HTTP_200_OK)

class GetLanguages(APIView):

    def get(self, request):
        return Response(data=all_categories, status=status.HTTP_200_OK)

class GetTrainingStatus(APIView):

    def get(self, request):
        current_status = TrainingStatus.objects.get(id=1)
        return Response(data=current_status.status, status=status.HTTP_200_OK)

class LoadModel(APIView):

    def get(self, request):
        try:
            global the_model
            the_model = torch.load("model.pkl")
            return Response(data={"successfully loaded model."}, status=status.HTTP_200_OK)
        except Exception:
            return Response(data={"unable to load model."}, status=status.HTTP_404_NOT_FOUND)