import time
from typing import List
from random import randint, choice
from .lib import User, Event
import numpy as np

try:
    import colorama
    from colorama import Back as B, Fore as F, Style
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.document import Document
    from prompt_toolkit.application.current import get_app
except ImportError as e:
    raise Exception(
        'Extra dependencies are required to use CLI tool. Use `pip install typegenie[with-cli]`').with_traceback(
        e.__traceback__)

colorama.init()


def color(text, fore=F.RESET, back=B.RESET, reset=True):
    if reset:
        return f'{fore}{back}{text}{Style.RESET_ALL}'
    else:
        return f'{fore}{back}{text}'


def printc(text, fore=F.WHITE, back=B.RESET, reset=True):
    print(color(text, fore, back, reset))


def text_changed(buffer):
    buffer.start_completion(select_first=False)


def pre_run():
    app = get_app()
    buff = app.current_buffer
    buff.start_completion(select_first=False)
    # print('In the test!')


class TypeGenieCompleter(Completer):
    def __init__(self, user: User, profiling=False):
        self.user = user
        self.context = None
        self.session_id = None
        self.records = None
        if profiling is True:
            self.records = []

    def get_completions(self, document: Document, complete_event):
        start = time.time()
        predictions = self.user.get_completions(session_id=self.session_id, events=self.context, query=document.text)
        end = time.time()
        elapsed_time = end - start
        if self.records is not None:
            self.records.append(elapsed_time)
        for p in predictions:
            yield Completion(p, start_position=0)

    def compute_statistics(self):
        if self.records is not None:
            print('Computing statistics with {} samples'.format(len(self.records)))
            avg = sum(self.records) / len(self.records)
            percentile25 = np.percentile(np.array(self.records), 25)
            percentile50 = np.percentile(np.array(self.records), 50)
            percentile75 = np.percentile(np.array(self.records), 75)
            percentile100 = np.percentile(np.array(self.records), 100)
            printc(
                "\nAverage: {}\nPercentile 25%: {}\nPercentile 50%: {}\nPercentile 75%: {}\nPercentile 100%: {} ".format(
                    avg, percentile25, percentile50, percentile75, percentile100))
            return

class AutoComplete:
    def __init__(self, user, dialogue_dataset, interactive=True, unprompted=False, multiline=False, profiling=False):
        self.user = user
        self.context = []
        self.dialogue_dataset = dialogue_dataset
        self.unprompted = unprompted
        self.multiline = multiline
        self.interactive = interactive
        self.profiling = profiling
        self.session = PromptSession(complete_in_thread=True,
                                     complete_while_typing=True,
                                     completer=TypeGenieCompleter(user=self.user, profiling=self.profiling))
        self.session.default_buffer.on_text_changed.add_handler(text_changed)

    def sample_context_and_response(self):
        while True:
            did = randint(0, len(self.dialogue_dataset) - 1)
            dialogue_events: List[Event] = self.dialogue_dataset[did].events

            agent_uids = [idx for idx, u in enumerate(dialogue_events) if u.author == 'AGENT' and u.event == 'MESSAGE']
            if len(agent_uids) > 0:
                break

        split_idx = int(choice(agent_uids))
        return dialogue_events[:split_idx], dialogue_events[split_idx:]

    def interact(self):
        while True:
            try:
                printc('-' * 100, fore=F.WHITE)
                context, remaining = self.sample_context_and_response()
                self.session.completer.session_id = self.user.create_session()
                self.render_context(context)
                self.context = context
                for i in range(len(remaining)):
                    event = remaining[i]
                    if event.event != 'MESSAGE':
                        continue

                    role, response = event.author, event.value
                    if role == 'AGENT':
                        printc('\nAgent actually said: ' + response, fore=F.BLUE)
                        new_response = self.get_prediction()
                        if len(new_response) > 0:
                            print("Just got a prediction: {}".format(new_response))
                            response = new_response
                    else:
                        printc('\nUser: ' + response, fore=F.YELLOW)

                    if not self.interactive:
                        break
                    event._value = response
                    self.context.append(event)

                printc('-' * 100, fore=F.WHITE)
            except KeyboardInterrupt:
                self.context = []
                printc('\nChat reset!', F.RED)
                printc('\nPress cntr + C again to exit', F.RED)
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    printc('\nExiting...', F.RED)
                    self.session.completer.compute_statistics()
                    return

    def render_context(self, context: List[Event]):
        for event in context:
            if event.event == 'MESSAGE':
                if event.author == 'USER':
                    printc('\nUser: ' + event.value, fore=F.YELLOW)
                elif event.author == 'AGENT':
                    printc('\nAgent: ' + event.value, fore=F.GREEN)

    def get_prediction(self):
        self.session.completer.context = self.context
        text = self.session.prompt('Agent (with TypeGenie): ', pre_run=pre_run if self.unprompted else None,
                                   multiline=self.multiline)
        return text
