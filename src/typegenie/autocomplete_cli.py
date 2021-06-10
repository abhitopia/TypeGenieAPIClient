import time
from typing import List

import colorama
from colorama import Back as B, Fore as F, Style
import numpy as np
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.application.current import get_app
from typegenie import User, Event

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
    def __init__(self, user: User):
        self.user = user
        self.context = None
        self.session_id = None

    def get_completions(self, document: Document, complete_event):
        predictions = self.user.get_completions(session_id=self.session_id, events=self.context, query=document.text)
        for p in predictions:
            yield Completion(p, start_position=0)


class AutoComplete:
    def __init__(self, user, dialogue_dataset, sampling_dist, interactive=True, unprompted=False):
        self.user = user
        self.context = []
        self.dialogue_dataset = dialogue_dataset
        self.unprompted = unprompted
        self.interactive = interactive
        self.sampling_dist = sampling_dist
        self.session = PromptSession(complete_in_thread=True,
                                     complete_while_typing=True,
                                     completer=TypeGenieCompleter(user=self.user))
        self.session.default_buffer.on_text_changed.add_handler(text_changed)

    def sample_context_and_response(self):
        while True:
            did = np.random.randint(len(self.dialogue_dataset))
            dialogue_events: List[Event] = self.dialogue_dataset[did].events

            agent_uids = [idx for idx, u in enumerate(dialogue_events) if u.author == 'AGENT' and u.event == 'MESSAGE']
            if len(agent_uids) > 0:
                break

        if self.sampling_dist == 'uniform':
            split_idx = int(np.random.choice(agent_uids))
        else:
            agent_idx = -1
            while agent_idx < 0 or agent_idx >= len(agent_uids):
                agent_idx = int(np.round(np.random.normal(len(agent_uids) / 2, len(agent_uids) / 4)))
            split_idx = agent_uids[agent_idx]

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
        text = self.session.prompt('Agent (with TypeGenie): ', pre_run=pre_run if self.unprompted else None)
        return text


# @click.command()
# @click.option('-md', '--model-dir', help="Model directory",
#               type=click.Path(dir_okay=True, exists=True, file_okay=False),
#               required=False, default="data/models/dgpt2bpttviasatv1/best_model")
# @click.option('-nb', '--num-beams', default=10, help="Number of beams", type=int)
# @click.option('-ng', '--num-beam-groups', default=None, type=int,
#               help="Number of groups, if not specified defaults to `num-beams`")
# @click.option('-dp', '--diversity-penalty', default=0.5, type=float,
#               help="Diversity penalty for Diversity promoting beam search")
# @click.option('-ngram', '--no-repeat-ngram-size', default=3, type=int, help="Ngram size to prevent repetition")
# @click.option('-mil', '--min-len', default=5, type=int, help="Minimum prediction length")
# @click.option('-mal', '--max-len', default=20, type=int, help="Maximum prediction length")
# @click.option('-dd', '--data-dir', help="Data directory", default='data/viasat_corrected')
# @click.option('-dn', '--dataset-name', help='Name of supported dataset', default='viasat', required=False,
#               type=click.Choice(['viasat', 'viasat_best', 'viasat_small', 'viasat_new']), show_default=True)
# @click.option('-cd', '--cache-dir', help="Cache directory", default='data/.cache')
# @click.option('-s', '--sampling-dist', help='Sampling function used', default='normal', required=False,
#               type=click.Choice(['uniform', 'normal']), show_default=True)
# @click.option('--interactive', is_flag=True, default=False, help="Set to continue interaction")
# @click.option('--with-scores', is_flag=True, default=False, help="Whether to show completion scores")
# @click.option('--unprompted', is_flag=True, default=False, help="Show completions even when unprompted")
# @click.option('--error-only', is_flag=True, default=False, help="Only show erroneous dialogues")
# def autocomplete(**options):
#     options = Box(options)
#
#     data_loader = LMDatasetLoader.get_loader(name=options.dataset_name,
#                                              data_dir=options.data_dir,
#                                              cache_dir=options.cache_dir,
#                                              split='validation')
#
#     # Get original text
#     dialogue_dataset = data_loader.get_dialogue_datasets()
#
#     if options.error_only:
#         options.sampling_dist = 'uniform'
#         error_file = Path(options.data_dir) / 'error_dialogues.pkl'
#         if not error_file.exists():
#             error_dialogues = []
#             for did in tqdm(range(len(dialogue_dataset))):
#                 corrected_dialogue = dialogue_dataset[did]['dialogue']
#                 org_dialogue = dialogue_dataset[did]['org_dialogue']
#                 dialogue = get_dialogue_diff(corrected_dialogue, org_dialogue)
#                 error_found = False
#                 for u in dialogue:
#                     if len(u[-1]) > 0:
#                         error_found = True
#                         break
#
#                 if error_found:
#                     error_dialogues.append(dialogue_dataset[did])
#             pickle.dump(error_dialogues, error_file.open('wb'))
#         else:
#             error_dialogues = pickle.load(error_file.open('rb'))
#         dialogue_dataset = error_dialogues
#
#     model = TypeGenie(model_path=options.model_dir, cache_path=options.cache_dir)
#
#     args = PredictionArgs(
#         num_beams=options.num_beams,
#         num_beam_groups=options.num_beam_groups if options.num_beam_groups is not None else options.num_beams,
#         diversity_penalty=options.diversity_penalty,
#         no_repeat_ngram_size=options.no_repeat_ngram_size,
#         min_length=options.min_len,
#         max_length=options.max_len,
#         num_return_sequences=options.num_beams
#     )

#     autocompleter = AutoComplete(model=model,
#                                  pred_args=args,
#                                  dialogue_dataset=dialogue_dataset,
#                                  sampling_dist=options.sampling_dist,
#                                  with_scores=options.with_scores,
#                                  unprompted=options.unprompted,
#                                  interactive=options.interactive)
#     autocompleter.interact()
#
#
# if __name__ == '__main__':
#     autocomplete()
