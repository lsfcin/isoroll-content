from _typeshed import Incomplete

MODELS: Incomplete
SOFT_CAP: Incomplete
OUTPUT_DIR: Incomplete
LEDGER_PATH: Incomplete
INBOX: Incomplete
OUTBOX: Incomplete

def generate(prompt, out_path, guide_path=None, alias: str = 'nb'): ...
def drop_manual(stem, prompt, guide_path): ...
def collect_manual(stem): ...
