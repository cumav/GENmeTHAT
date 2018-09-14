#!/usr/bin/env python
import os
import sys
import torch
import torch.nn as nn

if __name__ == '__main__':

    all_categories = ['Arabic', 'Chinese', 'Czech', 'Dutch', 'English', 'French', 'German', 'Greek', 'Irish', 'Italian',
                      'Japanese', 'Korean', 'Polish', 'Portuguese', 'Russian', 'Scottish', 'Spanish', 'Vietnamese']
    n_categories = len(all_categories)

    class RNN(nn.Module):
        def __init__(self, input_size, hidden_size, output_size):
            super(RNN, self).__init__()
            self.hidden_size = hidden_size

            self.i2h = nn.Linear(n_categories + input_size + hidden_size, hidden_size)
            self.i2o = nn.Linear(n_categories + input_size + hidden_size, output_size)
            self.o2o = nn.Linear(hidden_size + output_size, output_size)
            self.dropout = nn.Dropout(0.1)
            self.softmax = nn.LogSoftmax(dim=1)

        def forward(self, category, input, hidden):
            input_combined = torch.cat((category, input, hidden), 1)
            hidden = self.i2h(input_combined)
            output = self.i2o(input_combined)
            output_combined = torch.cat((hidden, output), 1)
            output = self.o2o(output_combined)
            output = self.dropout(output)
            output = self.softmax(output)
            return output, hidden

        def initHidden(self):
            return torch.zeros(1, self.hidden_size)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genme.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
