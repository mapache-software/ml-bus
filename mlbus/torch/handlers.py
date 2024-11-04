from mlbus.torch.commands import (
    Train,
    Evaluate,
    Iterate
)

def handle_train(command: Train):
    command.aggregate.phase = 'train'
    command.callback.phase = command.aggregate.phase
    command.callback.epoch = command.aggregate.epoch
    command.aggregate.fit(command.loader, command.callback)
    command.callback.flush()
    if command.count_epoch:
        command.aggregate.epoch += 1

def handle_evaluate(command: Evaluate):
    command.aggregate.phase = 'evaluate'
    command.callback.phase = command.aggregate.phase
    command.callback.epoch = command.aggregate.epoch
    command.aggregate.evaluate(command.loader, command.callback)
    command.callback.flush()
    if command.count_epoch:
        command.aggregate.epoch += 1

def handle_iterate(command: Iterate):
    for phase, loader in command.loaders:
        command.aggregate.phase = phase
        command.callback.phase = command.aggregate.phase
        command.callback.epoch = command.aggregate.epoch
        command.aggregate.fit(loader, command.callback) if phase == 'train' else command.aggregate.evaluate(loader, command.callback)
        command.callback.flush()
    if command.count_epoch:
        command.aggregate.epoch += 1