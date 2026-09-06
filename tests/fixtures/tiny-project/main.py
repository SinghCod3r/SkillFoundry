import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', help='foo help')
    args = parser.parse_args()
    print(args.foo)
if __name__ == '__main__':
    main()
