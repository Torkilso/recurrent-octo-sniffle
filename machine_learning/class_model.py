import intersect
import math, uuid, os
import numpy as np
import keras
from itertools import cycle
from PIL import Image, ImageDraw



class Boundingbox:
    def __init__(self, traces):
        
        max_x = 0
        min_x = math.inf
        max_y = 0
        min_y = math.inf

        for trace in traces:
            y = np.array(trace).astype(np.float)
            x, y = y.T

            if max_x < x.max():
                max_x = x.max()

            if max_y < y.max():
                max_y = y.max()

            if min_x > x.min():
                min_x = x.min()

            if min_y > y.min():
                min_y = y.min()
            
        self.mid_x = (max_x + min_x)/2
        self.mid_y = (max_y + min_y)/2
        self.max_x = max_x
        self.max_y = max_y
        self.min_x = min_x
        self.min_y = min_y
        self.width = max_x - min_x
        self.height = max_y - min_y
    
class Regular:
    def __init__(self, segmentgroup=None):
        self.segmentgroup = segmentgroup


class Fraction:
    def __init__(self, numerator=None, denomirator=None):
        self.numerator = numerator
        self.denomirator = denomirator


class Power:
    def __init__(self, base=None, exponent=None):
        self.base = base
        self.exponent = exponent

    def is_power(base, exponent):
        pass

class Trace:
    def __init__(self, points):
        self.points = points
        self.boundingbox = Boundingbox(points)

    def add_points(amount):
        pass

    def remove_points(amount):
        pass

    def check_overlap(trace):
        pass


class Segment:
    def __init__(self, traces, id):
        self.traces = traces
        self.boundingbox = Boundingbox(traces)
        self.id = id
        self.truth = ''

    def print_info(self):
        print("\nSegment info for", self.id)
        print("Truth:", self.truth)
        print("Amount of traces:", len(self.traces))
        print("Length of traces", [len(t) for t in self.traces])
        b = self.boundingbox
        print("Boundingbox (x, y, w, h):", b.mid_x, b.mid_y, b.width, b.height)
        print("max_x, min_x, max_y, min_y", b.max_x, b.min_x, b.max_y, b.min_y)

    def add_trace(trace):
        # might be useful for live feedback
        pass


class Segmentgroup:
    def __init__(self, segments):
        self.segments = segments

    

class Expression:
    def __init__(self):
        self.groups = []
        self.segments = dict()
        self.predictor = Predictor()
        

    def create_tracegroups(self, traces, trace_pairs):
        tracegroups = []       
        
        if len(trace_pairs) > 0:
            tracegroups.append(set(list(trace_pairs)[0]))

            for i, pair in enumerate(trace_pairs):
                
                for s in tracegroups:
                    if pair[0] in s:
                        s.add(pair[1])
                        break
                    else:
                        new_set = set()
                        new_set.add(pair[0])
                        new_set.add(pair[1])
                        tracegroups.append(new_set)
        
        for i, trace in enumerate(traces):
            found = False
            for group in tracegroups:
                if i in group:
                    found = True
            if not found:
                tracegroups.append(set([i]))
        
        sorted_tracegroups = sorted(tracegroups, key=lambda m:next(iter(m)))

        return sorted_tracegroups

    def find_overlap_pairs(self, traces):
        overlap_pairs = set()

        for i, trace in enumerate(traces[:-1]):
            for j, trace2 in enumerate(traces[i+1:]):
                for coord1 in trace:
                    for coord2 in trace2:
                        if math.hypot(coord2[0] - coord1[0], coord2[1] - coord1[1]) < 10:
                            overlap_pairs.add((i, i+j+1))

                # Check lines between endpoints
                overlap = intersect.intersect(trace[0], trace[-1], trace2[0], trace2[-1])
                if(overlap):
                    overlap_pairs.add((i, i+j+1))
        
        return overlap_pairs


    def feed_traces(self, traces):
        overlap_pairs = self.find_overlap_pairs(traces)  
        tracegroups = self.create_tracegroups(traces, overlap_pairs)
        self.create_segments(traces, tracegroups)

        #for id, segment in self.segments.items():
        #    segment.print_info()


    def create_segments(self, traces, tracegroups):
        for i, group in enumerate(tracegroups):
            traces_for_segment = [traces[j] for j in list(group)]
            id = str(i)
            segment = Segment(traces_for_segment, id)
            self.segments[id] = segment


    def join_segments(self, segment1, segment2):
        pass

    
    def find_segments_in_area(self, max_x, min_x, max_y, min_y):
        # Searches through segments and look for middle points inside area
        segments_in_area = []

        for id, segment in self.segments.items():
            if min_x <= segment.boundingbox.mid_x <= max_x and min_y <= segment.boundingbox.mid_y <= max_y:
                segments_in_area.append(segment.id)

        return segments_in_area


    def is_fraction(self, id):
        coords = self.segments[id].boundingbox
        
        over = self.find_segments_in_area(coords.max_x, coords.min_x, coords.min_y, coords.min_y - 200)
        under = self.find_segments_in_area(coords.max_x, coords.min_x, coords.max_y + 200, coords.max_y) 

        print('over', over)
        print('under', under)

        pass


    def is_equalsign(self, minus1, minus2):

        

        return True

    def classify_segments(self):

        minus_ids = []

        for id, segment in self.segments.items():
            segment.truth = self.predictor.predict(segment.traces)
            segment.print_info()

            if segment.truth == '-':
                minus_ids.append(segment.id)
        
        # Check if minus signs is fractions

        for minus_id in minus_ids:
            self.is_fraction(minus_id)




        #m1 = self.segments[minus_segments[0]]
        #m2 = self.segments[minus_segments[1]]
        
        #print('Equalsign:', self.is_equalsign(m1, m2))

        #if minus_count > 1:
        #    for id in minus_segments[:-1]:
                
         

    def search_horizontal(self):
        
        pass


    def create_segmentgroups(self):
        pass

class Predictor:
    MODEL_PATH = os.getcwd() + '/machine_learning/my_model.h5'
    CLASSES = os.listdir(os.getcwd() + '/machine_learning' + '/train')

    def __init__(self):
        self.model = keras.models.load_model(Predictor.MODEL_PATH)

    def predict(self, segment_traces):
        processed = self.pre_process(segment_traces)
        output = self.model.predict(processed, steps=1, batch_size=None, verbose=1)
        
        best_pred = (0, 0)
        
        for i, p in enumerate(output[0]):

            if p > best_pred[1]:
                best_pred = (i, p)
                prediction = Predictor.CLASSES[i]

        return prediction
        
    #https://gist.github.com/perrygeo/4512375
    def scale_linear_bycolumn(self, rawpoints, high=24, low=0, ma=0, mi=0):
        mins = mi
        maxs = ma

        rng = maxs - mins

        output = high - (((high - low) * (maxs - rawpoints)) / rng)

        return output

    def pre_process(self, traces):
        resolution = 24
        image_resolution = 26

        image = Image.new('L', (image_resolution, image_resolution), "white")
        draw = ImageDraw.Draw(image)

        max_x = 0
        min_x = math.inf
        max_y = 0
        min_y = math.inf


        for trace in traces:
            y = np.array(trace).astype(np.float)
            x, y = y.T

            if max_x < x.max():
                max_x = x.max()

            if max_y < y.max():
                max_y = y.max()

            if min_x > x.min():
                min_x = x.min()

            if min_y > y.min():
                min_y = y.min()

        width = max_x - min_x
        height = max_y - min_y
        scale = width / height

        width_scale = 0
        height_scale = 0

        if scale > 1:
            # width > height
            height_scale = resolution / scale
        else:
            # width < height
            width_scale = resolution * scale

        for trace in traces:

            y = np.array(trace).astype(np.float)

            x, y = y.T

            if width_scale > 0:
                # add padding in x-direction
                new_y = self.scale_linear_bycolumn(y, high=resolution, low=0, ma=max_y, mi=min_y)
                side = (resolution - width_scale) / 2
                new_x = self.scale_linear_bycolumn(x, high=(resolution - side), low=(side), ma=max_x, mi=min_x)
            else:
                # add padding in y-direction
                new_x = self.scale_linear_bycolumn(x, high=resolution, low=0, ma=max_x, mi=min_x)  # , maximum=(max_x, max_y), minimum=(min_x, min_y))
                side = (resolution - height_scale) / 2
                new_y = self.scale_linear_bycolumn(y, high=(resolution - side), low=(side), ma=max_y, mi=min_y)  # , maximum=(max_x, max_y), minimum=(min_x, min_y))

            coordinates = list(zip(new_x, new_y))
            xy_cycle = cycle(coordinates)

            next(xy_cycle)

            for x_coord, y_coord in coordinates[:-1]:
                next_coord = next(xy_cycle)
                draw.line([x_coord, y_coord, next_coord[0], next_coord[1]], fill="black", width=1)


        i = image.convert('LA')

        arr = np.asarray(i)

        formatted = []
        for row in arr:
            new_row = []
            for col in row:
                new_row.append(col[0])

            formatted.append(new_row)

        return np.asarray([np.asarray(formatted).reshape((26, 26, 1))])

if __name__ == '__main__':
    pass
