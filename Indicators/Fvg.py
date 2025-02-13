from Utils import num_func as nf

class Fvg():

    FVG_DELTA_THRESHOLD = 2

    def __init__(self):
        self.fvg_tracker = {
            'delta_p': [],
            'delta_n': [],
        }

    def cycle_chunk(self, chunk):
        self.chunk = chunk
        for i in range(-600, 1, 1):
            try:
                # Index through all data taking 3 at a time
                self.get_movement_delta(chunk, i)
            except Exception as e:
                raise

        self.remove_invalidated_fvg_zones()

        return self.fvg_tracker

        # Compare gradient both directions
        # if we have a criteria met we then check n-1 of n=3 meets following:
        # Negative gradient:
        # low of n=1 is greater than high of n=3 and greater than a set threshold
        # Positive gradient:
        # low of n=3 is higher than high of n=1 and greater than a set threshold
        # Store the locations of the fvg entry and exit price and if theyre + or -
        # Then we will need to findout which of these fvg's have been invalidated
        # Simply look for any closes within data chunk that have either gone over - fvg's
        # or under + fvg's
        # then we look at current time frame and run the following checks/scenarios

    def remove_invalidated_fvg_zones(self):
        # Go through all the fvgs in delta_p/n
        # Take the index of the fvg start in the chunk
        # and see if the price level at each index after the start
        # of the fvg closes below the bottom oft he fvg for delta_p
        # and if the candle closes above the fvg for delta_n
        for idx, x in enumerate(self.fvg_tracker['delta_p']):
            self.fvg_tracker['delta_p'][idx]['fvg_invalidated'] = False
            for i in range(x['fvg_chunk_index'], 1, 1):
                if self.chunk.close[i] < x['fvg_low']:
                    # Mark as invalidated
                    self.fvg_tracker['delta_p'][idx]['fvg_invalidated'] = True
                    break

        for idx, x in enumerate(self.fvg_tracker['delta_n']):
            self.fvg_tracker['delta_n'][idx]['fvg_invalidated'] = False
            for i in range(x['fvg_chunk_index'], 1, 1):
                if self.chunk.close[i] > x['fvg_high']:
                    # Mark as invalidated
                    self.fvg_tracker['delta_n'][idx]['fvg_invalidated'] = True
                    break

    def get_movement_delta(self, chunk, index) -> int:
        # Signifies bull FVG
        if chunk.high[index] < chunk.low[index+2] and chunk.high[index] > chunk.open[index+1] and chunk.low[index+2] < chunk.close[index+1]:
            if nf.pct_delta(chunk.high[index], chunk.low[index+2]) >= self.FVG_DELTA_THRESHOLD:
                self.fvg_tracker['delta_p'].append({
                    'fvg_high': chunk.low[index+2],
                    'fvg_low': chunk.high[index],
                    'fvg_timestamp': chunk.datetime.date(index),
                    'fvg_chunk_index': index+2
                })
        # Signifies bear FVG
        if chunk.low[index] > chunk.high[index+2] and chunk.low[index] < chunk.open[index+1] and chunk.high[index+2] > chunk.close[index+1]:
            if nf.pct_delta(chunk.high[index+2], chunk.low[index]) >= self.FVG_DELTA_THRESHOLD:
                self.fvg_tracker['delta_n'].append({
                    'fvg_high': chunk.low[index],
                    'fvg_low': chunk.high[index+2],
                    'fvg_timestamp': chunk.datetime.date(index),
                    'fvg_chunk_index': index+2
                })
