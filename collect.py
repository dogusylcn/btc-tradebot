if __name__ == "__main__":
    from subprocess import Popen
    from time import sleep
    import os
    cwd = os.getcwd()
    Popen("python {}\\data\\collect_txs.py".format(cwd))
    Popen("python {}\\data\\collect_rates.py".format(cwd))
    Popen("python {}\\data\\make_data.py".format(cwd))

