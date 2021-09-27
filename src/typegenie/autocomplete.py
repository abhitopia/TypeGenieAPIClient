import time

from typing import List, Optional
from random import randint, choice

from .lib import User, Event


try:
    import colorama
    from colorama import Back as B, Fore as F, Style
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.document import Document
    from prompt_toolkit.application.current import get_app

    from prompt_toolkit.auto_suggest import Suggestion
    from prompt_toolkit.key_binding import KeyBindings
except ImportError as e:
    raise Exception('Extra dependencies are required to use CLI tool. Use `pip install typegenie[with-cli]`').with_traceback(e.__traceback__)

colorama.init()

bindings = KeyBindings()

def color(text, fore=F.RESET, back=B.RESET, reset=True):
    if reset:
        return f'{fore}{back}{text}{Style.RESET_ALL}'
    else:
        return f'{fore}{back}{text}'


def printc(text, fore=F.WHITE, back=B.RESET, reset=True):
    print(color(text, fore, back, reset))


def text_changed(buffer):
    buffer.start_completion(select_first=True)


def go_to_completion(self, index: Optional[int]) -> None:
    """
    NOTE: This over-rides prevents Document to be changes as we scroll over completions
    Select a completion from the list of current completions.
    """
    assert self.complete_state

    # Set new completion
    state = self.complete_state
    state.go_to_index(index)

    # Note: We skipped the next steps
    # Set text/cursor position
    # new_text, new_cursor_position = state.new_text_and_position()
    # self.document = Document(new_text, new_cursor_position)

    # Instead we set a suggestion for the selected completion
    if index is not None:
        text = self.complete_state.current_completion.text
        self.suggestion = Suggestion(text=text)
        self.on_suggestion_set.fire()

    # (changing text/cursor position will unset complete_state.)
    self.complete_state = state


@bindings.add('tab')
def _(event):
    """Full Accept """
    buffer = event.app.current_buffer
    if buffer.suggestion is not None:
        buffer.insert_text(buffer.suggestion.text)


def partial_accept(event):
    buffer = event.app.current_buffer
    if buffer.suggestion is not None:
        text = buffer.suggestion.text
        text_split = text.split(' ')
        add = text_split[0]
        add = add + ' ' if len(text_split) > 0 else add
        buffer.insert_text(add)


@bindings.add('s-tab', is_global=True)
def _(event):
    """Partial Accept"""
    partial_accept(event)


@bindings.add('s-right', is_global=True)
def _(event):
    """Partial Accept"""
    partial_accept(event)


def pre_run_unprompted():
    app = get_app()
    buff = app.current_buffer
    buff.start_completion(select_first=False)
    buff.on_text_changed.add_handler(text_changed)
    # This line enabled showing completions like TypeGenie
    buff.go_to_completion = go_to_completion.__get__(buff)


def pre_run():
    app = get_app()
    buff = app.current_buffer
    buff.on_text_changed.add_handler(text_changed)
    # This line enabled showing completions like TypeGenie
    buff.go_to_completion = go_to_completion.__get__(buff)


class TypeGenieCompleter(Completer):
    def __init__(self, user: User):
        self.user = user
        self.context = None
        self.session_id = None

    def get_completions(self, document: Document, complete_event):
        predictions = self.user.get_completions(session_id=self.session_id, events=self.context, query=document.text)
        for p in predictions:
            yield Completion(p, start_position=0)


class AutoComplete:

    def __init__(self, user, dialogue_dataset, interactive=True, unprompted=False, multiline=False, no_context=False):
        self.user = user
        self.context = []
        self.dialogue_dataset = dialogue_dataset
        self.unprompted = unprompted
        self.multiline = multiline

        self.no_context = no_context
        self.interactive = interactive
        self.session = PromptSession(complete_in_thread=True,
                                     complete_while_typing=True,
                                     completer=TypeGenieCompleter(user=self.user))

    def sample_context_and_response(self):
        while True:
            did = randint(0, len(self.dialogue_dataset)-1)
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
                if not self.no_context:
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
                            response = new_response
                    else:
                        printc('\nUser: ' + response, fore=F.YELLOW)

                    if not self.interactive:
                        break
                    event._value = response
                    if not self.no_context:
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
                    return

    def render_context(self, context: List[Event]):
        for event in context:
            if event.event == 'MESSAGE':
                if event.author == 'USER':
                    printc('\nUser: ' + event.value, fore=F.YELLOW)
                elif event.author == 'AGENT':
                    printc('\nAgent: ' + event.value, fore=F.GREEN)

    def get_prediction(self):
        if self.no_context:
            self.session.completer.context = []
        else:
            self.session.completer.context = self.context
        text = self.session.prompt('Agent (with TypeGenie): ',
                                   pre_run=pre_run_unprompted if self.unprompted else pre_run,
                                   key_bindings=bindings,
                                   multiline=self.multiline)
        return text

