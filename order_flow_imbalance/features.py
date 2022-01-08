import numpy as np
import pandas as pd
from tqdm import tqdm
import db_lob as lob
import argparse
import logging 

parser = argparse.ArgumentParser()
parser.add_argument("--data", default='../data/2505133.csv', help="filename.", type=str)
parser.add_argument("--volume_threshold", default=1000000, help="Volume threshold", type=int)
parser.add_argument("--ticksize", default=0.0001, help="ticksize", type=float)
parser.add_argument("--maxlevel", default=10, help="maximum level of the book to study", type=int)
parser.add_argument("--data_frac", default=1, help="fraction of messages to read", type=float)

def main(data, volume_threshold, ticksize, maxlevel, data_frac):
    """
    
    """

    messages = lob.parse_FullMessages(data)
    book = lob.LimitOrderBook(volume_threshold, ticksize)

    bid_prices, bid_volumes, ask_prices, ask_volumes, time, mid_price = [],[],[],[],[],[]

    n_msg = int(len(messages) * data_frac)
    for msg in tqdm(messages[:n_msg], desc="Reconstructing the book"):
        bars = book.generic_incremental_update(msg)
        ask_side, bid_side = book.askTree, book.bidTree

        if not (any(ask_side) and any(bid_side)): continue
        
        a = list(ask_side.values())
        b = list(bid_side.values())

        if len(a) < maxlevel or len(b) < maxlevel: continue
        time.append(book.datetime)
        a = a[:maxlevel]
        b = b[:maxlevel]

        ask_prices.append([x.price for x in a])
        ask_volumes.append([x.totalVolume for x in a])
        bid_prices.append([x.price for x in b])
        bid_volumes.append([x.totalVolume for x in b])
        mid_price.append(np.abs(a[0].price-b[0].price)/ticksize)
    
    df = pd.DataFrame(time,columns=['time'])
    df['ask_volumes'] = ask_volumes
    df['ask_prices'] = ask_prices
    df['bid_prices'] = bid_prices
    df['bid_volumes'] = bid_volumes
    df['mid_price'] = mid_price

    import os
    dir = '../data_cleaned'
    if os.path.isdir(dir)==False:
            os.mkdir(dir)
    df.to_csv(dir+'/time_evolution_{}_levels.csv'.format(maxlevel), index=False)

if __name__ == "__main__":
    args = vars(parser.parse_args())
    main(**args)


