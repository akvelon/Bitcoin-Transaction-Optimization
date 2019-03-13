"""
Copyright 2019 Akvelon Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the License for the specific language governing permissions and limitations under the License.
"""
import argparse
import tensorflow as tf
from trainer import PredictorTrainer

parser = argparse.ArgumentParser()
parser.add_argument('--train', default=False, action='store_true',
                    help='do training')
parser.add_argument('--predict', default=False, action='store_true',
                    help='predict fee')
parser.add_argument('--evaluate_block', default='', type=str, help='model dir name')
parser.add_argument('--evaluate', default=False, action='store_true', help='evaluating the model on test data')
parser.add_argument('--test_data', default='', type=str, help='test data')
parser.add_argument('--batch_size', default=PredictorTrainer.BATCH_SIZE, type=int, help='batch size')
parser.add_argument('--train_steps', default=PredictorTrainer.TRAIN_STEPS, type=int,
                    help='number of training steps')


def main(argv):
    args = parser.parse_args(argv[1:])
    trainer = PredictorTrainer(args.batch_size, args.train_steps)

    if args.train is True:
        trainer.train()

    if args.evaluate:
        trainer.evaluate()

    if args.evaluate_block:
        trainer.evaluate_block(args.evaluate, args.test_data)

    if args.predict is True:
        print(trainer.predict([[0, 23.99160099, 9826, 1], [0, 7.46830273, 2338, 0]], [6.15, 1.01], '20190125-131755'))


if __name__ == '__main__':
    tf.app.run(main)
