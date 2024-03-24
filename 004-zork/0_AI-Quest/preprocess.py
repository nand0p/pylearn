import pickle
from transformers import *
from torch.utils.data import DataLoader, random_split, ConcatDataset, Dataset, Subset
import torch
from torch.nn.utils.rnn import pad_sequence
import random
import numpy as np


def load_dataset(train_file, test_file, batch_size, seq_len, special_tokens, tokenizer, model_type):
    
    # Gets dataset for given model
    if model_type == "gpt2":
        total_dataset = GPTDataset(train_file, test_file, tokenizer, seq_len)
    elif model_type == "bert":
        total_dataset = BertDataset(train_file, test_file, tokenizer, seq_len)
    elif model_type == "cross":
        total_dataset = CrossDataset(train_file, test_file, tokenizer, seq_len, batch_size)

    # Builds data loaders
    if test_file != None:
        train_indices = list(range(0, total_dataset.num_train_examples))
        test_indices = list(range(total_dataset.num_train_examples, len(total_dataset)))
        train_dataset = Subset(total_dataset, train_indices)
        test_dataset = Subset(total_dataset, test_indices)
    else:
        if model_type != "cross":
            split_size = int(len(total_dataset) * 0.9)
            train_dataset, test_dataset = random_split(total_dataset, [split_size, len(total_dataset) - split_size])
        else:
            split_index = int((len(total_dataset) / batch_size) * 0.9) * batch_size
            train_indices = list(range(0, split_index))
            test_indices = list(range(split_index, len(total_dataset)))
            train_dataset = Subset(total_dataset, train_indices)
            test_dataset = Subset(total_dataset, test_indices)


    shuffle_train = (model_type != "cross")
    train_loader = DataLoader(train_dataset, batch_size, shuffle=shuffle_train)
    test_loader = DataLoader(test_dataset, batch_size, shuffle=False)
    return train_loader, test_loader


def convert_episode_context_to_data_point(episode):
    # Gets context for the entire scene
    data_point = ' <|setting_name|> ' + episode['setting']['name'] + ", " + episode['setting']['category']
    data_point += ' <|setting_desc|> ' + episode['setting']['description']
    data_point += ' <|partner_name|> ' + episode['agents'][1]['name']
    data_point += ' <|self_name|> ' + episode['agents'][0]['name']
    data_point += ' <|partner_persona|> ' + episode['agents'][1]['persona']
    data_point += ' <|self_persona|> ' + episode['agents'][0]['persona']
    partner = episode['agents'][1]['name']
    self_character = episode['agents'][0]['name']

    # We can join the data_points together
    return data_point, partner, self_character


def get_previous_utterances(episode, response_num, partner):
    # builds speech over conversation
    res = ''
    if episode['character'][response_num] == partner:
        res += ' <|partner_say|> ' + episode['speech'][response_num]
        if episode['action'][response_num] is not None:
            res += ' <|partner_act|> ' + episode['action'][response_num]
        if episode['emote'][response_num] is not None:
            res += ' <|partner_emote|> ' + episode['emote'][response_num]
    else:
        res += ' <|self_say|> ' + episode['speech'][response_num]
        if episode['action'][response_num] is not None:
            res += ' <|self_act|> ' + episode['action'][response_num]
        if episode['emote'][response_num] is not None:
            res += ' <|self_emote|> ' + episode['emote'][response_num]
    return res


def random_sample(data, p=0.1):
    '''
    Samples randomly from a list like object.
    :param data: list representing data
    :param p: float in the range [0,1] representing percentage to select
    '''

    assert 0 <= p <= 1
    num_datapoints = len(data)
    indices = list(np.random.choice(num_datapoints, int(p*num_datapoints)))
    data = [data[i] for i in indices]
    return data

# For GPT2 LM
class GPTDataset(Dataset):
    def __init__(self, train_file, test_file, tokenizer, seq_len, n_history = 3, p = 0.1):
        """
        Creates the dataset for use with GPT.
        :param train_file: filepath of the train file
        ;param test_file: filepath of the test file
        :param tokenizer: pretrained tokenizer
        :param seq_len: max sequence length
        :param n_history: number of utterances before the current conversation to save
        :param p: percentage of the dataset to randomly sample
        """
        
        self.tokenizer = tokenizer
        self.max_seq_len = seq_len
        self.n_history = n_history
        self.p = p

        self.seq = []
        self.lengths = []
        self.masks = []

        self.convert_file(train_file)
        if test_file != None:
            self.num_train_examples = len(self.lengths)
            self.convert_file(test_file)

    def convert_file(self, file_name):
        with open(file_name, 'rb') as fp:
            data = pickle.load(fp)

            # Random sample from dataset
            data = random_sample(data, self.p)

            for episode in data:
                context, partner, self_character = convert_episode_context_to_data_point(episode)
                num_responses = len(episode['character'])
                previous_text = []
                for i in range(1, num_responses):

                    # objects for current call and response
                    current_input = context
                    for obj in episode['room_objects'][i]:
                        current_input += '<|object_desc|> ' + obj + " : " + episode['all_descriptions'][obj]

                    # previous text in conversation
                    previous_text += [get_previous_utterances(episode, i - 1, partner)]
                    current_input += ' '.join(previous_text[max(0, len(previous_text)-self.n_history):])

                    speech_input = current_input + ' <|task_speech|> ' + episode['speech'][i]
                    total_tokens = len(speech_input)
                    encoded = self.tokenizer.encode_plus(speech_input, max_length=self.max_seq_len, pad_to_max_length=True)
                    self.seq.append(torch.tensor(encoded['input_ids']))
                    self.masks.append(torch.tensor(encoded['attention_mask']))
                    self.lengths.append(total_tokens)
                    

                    second_persona_action = episode['action'][i]
                    second_persona_emote = episode['emote'][i]
                    if second_persona_action is not None:
                        action_input = current_input + ' <|task_action|> ' + second_persona_action
                        total_tokens = len(action_input)
                        encoded = self.tokenizer.encode_plus(action_input, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.seq.append(torch.tensor(encoded['input_ids']))
                        self.masks.append(torch.tensor(encoded['attention_mask']))
                        self.lengths.append(total_tokens)

                    if second_persona_emote is not None:
                        emote_input = current_input + ' <|task_emote|> ' + second_persona_emote
                        total_tokens = len(emote_input)
                        encoded = self.tokenizer.encode_plus(emote_input, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.seq.append(torch.tensor(encoded['input_ids']))
                        self.masks.append(torch.tensor(encoded['attention_mask']))
                        self.lengths.append(total_tokens)
                        

    def __len__(self):
        return len(self.lengths)

    def __getitem__(self, idx):
        item = {
            "seq": self.seq[idx],
            "lengths": self.lengths[idx],
            "mask":  self.masks[idx]
        }
        return item


def get_random_label(data, task):
    episode = random.choice(data)
    dist = list(episode[task])
    filtered = list(filter(None, dist))
    if len(filtered) == 0:
        return "UNK"
    else:
        return random.choice(filtered)

    
# Used for Bert Biranker
class BertDataset(Dataset):
    def __init__(self, train_file, test_file, tokenizer, seq_len, n_history = 3, p=0.1):
        """
        Creates the dataset for use with GPT.
        :param train_file: filepath of the train file
        :param test_file: filepath of the test file
        :param tokenizer: pretrained tokenizer
        :param seq_len: max sequence length
        :param n_history: number of utterances before the current conversation to save
        :param p: percentage of the dataset to randomly sample
        """
        self.tokenizer = tokenizer
        self.n_history = n_history
        self.p = p

        self.context = []
        self.input = []
        self.context_masks = []
        self.input_masks = []
        self.labels = []
        self.max_seq_len = seq_len

        self.convert_file(train_file)
        if test_file != None:
            self.num_train_examples = len(self.labels)
            self.convert_file(test_file)


    def convert_file(self, file_name):
        with open(file_name, 'rb') as fp:
            data = pickle.load(fp)

            # Randomly samples from the dataset
            data = random_sample(data)

            for episode in data:
                context, partner, self_character = convert_episode_context_to_data_point(episode)
                num_responses = len(episode['character'])
                previous_text = []
                for i in range(1, num_responses):
                    current_input = context
                    for obj in episode['room_objects'][i]:
                        current_input += '<|object_desc|> ' + obj + " : " + episode['all_descriptions'][obj]

                    previous_text += [get_previous_utterances(episode, i - 1, partner)]
                    current_input += ' '.join(previous_text[max(0, len(previous_text)-self.n_history):])

                    encoded = self.tokenizer.encode_plus('<|task_speech|> ' + current_input, max_length=self.max_seq_len, pad_to_max_length=True)
                    self.context.append(torch.tensor(encoded['input_ids']))
                    self.context_masks.append(torch.tensor(encoded['attention_mask']))


                    if random.random() > 0.5:
                        # Correct speech
                        correct_utterance = episode['speech'][i]
                        encoded = self.tokenizer.encode_plus(correct_utterance, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.input.append(torch.tensor(encoded['input_ids']))
                        self.input_masks.append(torch.tensor(encoded['attention_mask']))
                        self.labels.append(1)
                    else:
                        # Random incorrect speech
                        random_utterance = get_random_label(data, 'speech')
                        encoded = self.tokenizer.encode_plus(random_utterance, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.input.append(torch.tensor(encoded['input_ids']))
                        self.input_masks.append(torch.tensor(encoded['attention_mask']))
                        self.labels.append(-1)
                    

                    second_persona_action = episode['action'][i]
                    if second_persona_action is not None:
                        encoded = self.tokenizer.encode_plus('<|task_action|> ' + current_input, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.context.append(torch.tensor(encoded['input_ids']))
                        self.context_masks.append(torch.tensor(encoded['attention_mask']))

                        if random.random() > 0.5:
                            # Correct action
                            encoded = self.tokenizer.encode_plus(second_persona_action, max_length=self.max_seq_len, pad_to_max_length=True)
                            self.input.append(torch.tensor(encoded['input_ids']))
                            self.input_masks.append(torch.tensor(encoded['attention_mask']))
                            self.labels.append(1)
                        else:
                            # Incorrect random action
                            random_action = get_random_label(data, 'action')
                            encoded = self.tokenizer.encode_plus(random_action, max_length=self.max_seq_len, pad_to_max_length=True)
                            self.input.append(torch.tensor(encoded['input_ids']))
                            self.input_masks.append(torch.tensor(encoded['attention_mask']))
                            self.labels.append(-1)

                        
                    second_persona_emote = episode['emote'][i]
                    if second_persona_emote is not None:
                        encoded = self.tokenizer.encode_plus('<|task_emote|> ' + current_input, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.context.append(torch.tensor(encoded['input_ids']))
                        self.context_masks.append(torch.tensor(encoded['attention_mask']))

                        if random.random() > 0.5:
                            # Correct emote
                            encoded = self.tokenizer.encode_plus(second_persona_emote, max_length=self.max_seq_len, pad_to_max_length=True)
                            self.input.append(torch.tensor(encoded['input_ids']))
                            self.input_masks.append(torch.tensor(encoded['attention_mask']))
                            self.labels.append(1)
                        else:
                            # Incorrect random action
                            random_emote = get_random_label(data, 'emote')
                            encoded = self.tokenizer.encode_plus(random_emote, max_length=self.max_seq_len, pad_to_max_length=True)
                            self.input.append(torch.tensor(encoded['input_ids']))
                            self.input_masks.append(torch.tensor(encoded['attention_mask']))
                            self.labels.append(-1)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {
            "context": self.context[idx],
            "input": self.input[idx],
            "context_mask":  self.context_masks[idx],
            "input_mask":  self.input_masks[idx],
            "label": self.labels[idx]
        }
        return item


# Classification cross ranker.
# As is currently works for just emotes. 
class CrossDataset(Dataset):
    def __init__(self, train_file, test_file, tokenizer, seq_len, batch_size, n_history = 3, p=0.1):
        self.tokenizer = tokenizer
        self.n_history = n_history
        self.p = p

        
        self.seq = []
        self.masks = []
        self.labels = []
        self.position_ids = []
        self.max_seq_len = seq_len
        self.batch_size = batch_size

        self.emotes_strings = ["applaud", "blush", "cry", "dance", "frown", "gasp", "grin", "groan", "growl", "laugh", "nod", "nudge", "ponder", "pout", "scream", "shrug", "sigh", "smile", "stare", "wave", "wink", "yawn"]
        self.emotes_ids = self.tokenizer.convert_tokens_to_ids(self.emotes_strings)

        self.convert_file(train_file)
        if test_file != None:
            self.num_train_examples = len(self.labels)
            self.convert_file(test_file)

    def convert_file(self, file_name):
        with open(file_name, 'rb') as fp:
            data = pickle.load(fp)

            # Randomly samples from the dataset
            data = random_sample(data)

            for episode in data:
                context, partner, self_character = convert_episode_context_to_data_point(episode)   
                num_responses = len(episode['character'])
                previous_text = []
                for i in range(1, num_responses):
                    second_persona_emote = episode['emote'][i]
                    previous_text += [get_previous_utterances(episode, i - 1, partner)]

                    if second_persona_emote is not None:
                        current_input = context
                        for obj in episode['room_objects'][i]:
                            current_input += '<|object_desc|> ' + obj + " : " + episode['all_descriptions'][obj]
                        current_input += ' '.join(previous_text[max(0, len(previous_text)-self.n_history):])
                        num_context_tokens = len(current_input.split())

                        # Correct emote
                        encoded = self.tokenizer.encode_plus(current_input + second_persona_emote, max_length=self.max_seq_len, pad_to_max_length=True)
                        self.seq.append(torch.tensor(encoded['input_ids']))
                        self.masks.append(torch.tensor(encoded['attention_mask']))
                        self.labels.append(0)
                        zeros = torch.zeros(min(self.max_seq_len, num_context_tokens))
                        ones = torch.ones(max(0, self.max_seq_len - num_context_tokens))
                        self.position_ids.append(torch.cat((zeros, ones)))

                        # Batch size minus one random emotes
                        emote_random_sample = random.sample(self.emotes_strings, self.batch_size - 1)
                        for e in emote_random_sample:
                            encoded = self.tokenizer.encode_plus(current_input + " <SEP> " + e, max_length=self.max_seq_len, pad_to_max_length=True)
                            self.seq.append(torch.tensor(encoded['input_ids']))
                            self.masks.append(torch.tensor(encoded['attention_mask']))
                            self.labels.append(1)
                            zeros = torch.zeros(min(self.max_seq_len, num_context_tokens))
                            ones = torch.ones(max(0, self.max_seq_len - num_context_tokens))
                            self.position_ids.append(torch.cat((zeros, ones)))
                            


    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {
            "seq": self.seq[idx],
            "mask":  self.masks[idx],
            "position_ids":  self.position_ids[idx],
            "label": self.labels[idx]
        }
        return item