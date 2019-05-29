import argparse
import random
import sys

sys.path.append('/data/rishabh/')
sys.path.append('/Users/apple/MEngProject/')


def get_parser():
    parser = argparse.ArgumentParser(description='Run experiments on a dataset')

    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument('--encoder', type=str,
                        choices=['cnn', 'lstm', 'average', 'all'],
                        required=True)
    parser.add_argument('--attention', type=str, choices=['tanh', 'dot', 'all'],
                        required=True)
    parser.add_argument('--seeds', nargs='?', default='[1,1024,2**30,43,789]',
                        help='Seeds for runs.')
    parser.add_argument('--swa', nargs='?', default='[0,0,0,0,0,0]',
                        help='Enable Stochastic Weighted Averaging (use SWA?, start iter, frequency, ignore running norm, greater-than running norm, running norm-threshold).')
    parser.add_argument("--temp", type=float, default=1)

    parser.add_argument("--iters", type=int, default=20)

    parser.add_argument("--name", type=str, default='')

    parser.add_argument("--loss", type=int, default=0)
    return parser


if __name__ == "__main__":

    args, extras = get_parser().parse_known_args()
    args.extras = extras

    from Transparency.Trainers.DatasetQA import *
    from Transparency.ExperimentsQA import *
    from common_code.common import pickle_to_file

    dataset = datasets[args.dataset](args)

    if args.output_dir is not None:
        dataset.output_dir = args.output_dir

    encoders = ['cnn', 'lstm', 'average'] if args.encoder == 'all' else [
        args.encoder]

    seeds = eval(args.seeds)

    all_outputs = []
    for pseudo_random_seed in seeds:
        os.environ['PYTHONHASHSEED'] = str(pseudo_random_seed)
        np.random.seed(pseudo_random_seed)
        random.seed(pseudo_random_seed)
        torch.manual_seed(pseudo_random_seed)
        preds, atns, preds_lst, atns_lst = [], [], [], []

        if args.attention in ['tanh', 'all']:
            preds, atns = train_dataset_and_get_atn_map(
                dataset, encoders, args.iters)
            # generate_graphs_on_encoders(dataset, encoders)
        if args.attention in ['dot', 'all']:
            encoders = [e + '_dot' for e in encoders]
            preds, atns = train_dataset_and_get_atn_map(
                dataset, encoders, args.iters)
            # generate_graphs_on_encoders(dataset, encoders)
        all_outputs.append((preds, atns))

    run_settings_str = args.name + args.swa + args.seeds + str(
        args.attention) + str(args.dataset) + str(args.encoder) + str(args.temp)
    file_name = "stability-outputs-" + run_settings_str + ".pkl"
    pickle_to_file(all_outputs, file_name)