import math, keras
from itertools import cycle
import numpy as np
from PIL import Image, ImageDraw

class Boundingbox:
    def __init__(self, traces):
        max_x = 0
        min_x = math.inf
        max_y = 0
        min_y = math.inf

        x_in_max_y = 0

        for trace in traces:
            y = np.array(trace).astype(np.float)
            x, y = y.T

            if max_x < x.max():
                max_x = x.max()

            if max_y < y.max():
                max_y = y.max()
                indexes = np.nonzero(y == max_y)
                x_in_max_y = x[indexes[0][-1]]

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
        self.x_in_max_y = x_in_max_y


class Segment:
    def __init__(self, id, truth, traces):
        self.id = id
        self.traces = traces
        self.boundingbox = Boundingbox(traces)
        self.truth = truth

    def to_latex(self):
        return self.truth


class Group:
    def __init__(self, id, traces):
        self.id = id
        self.traces = traces
        self.boundingbox = Boundingbox(traces)
            
    def to_latex(self):

        latex = ''

        if type(self) == Segmentgroup:

            for obj in self.objects:
                latex += obj.to_latex()

        elif type(self) == Fraction:
            
            latex += '\\frac{'
            
            for obj in self.numerator:
                latex += obj.to_latex()

            latex += '}{'

            for obj in self.denominator:
                latex += obj.to_latex()

            latex += '}'

        elif type(self) == Power:

            for obj in self.base:
                latex += obj.to_latex()
            
            latex += '^{'

            for obj in self.exponent:
                latex += obj.to_latex()
            
            latex += '}'

        elif type(self) == Root:

            latex += '\\sqrt{'

            for obj in self.core:
                latex += obj.to_latex()

            latex += '}'

        return latex


class Segmentgroup(Group):
    def __init__(self, id, objects):
        super().__init__(id)
        self.objects = objects


    def add_object(self, obj):
        self.objects.append(obj)


    def to_latex(self):
        return super().to_latex()

        
class Fraction(Group):
    def __init__(self, id, mid_x, numerator, denominator):
        super().__init__(id, mid_x)
        self.numerator = numerator
        self.denominator = denominator

    def to_latex(self):
        return super().to_latex()


class Power(Group):
    def __init__(self, id, mid_x, base, exponent):
        super().__init__(id, mid_x)
        self.base = base
        self.exponent = exponent

    def to_latex(self):
        return super().to_latex()


class Root(Group):
    def __init__(self, id, core, root_traces):

        traces = root_traces
        for obj in core:
            traces = traces + obj.traces
            
        super().__init__(id, traces)
        self.core = core

    def to_latex(self):
        return super().to_latex()


class Sum(Group):
    def __init__(self, id, mid_x, body):
        super().__init__(id, mid_x)
        self.body = body

    def to_latex(self):
        return super().to_latex()


class Integral(Group):
    pass


class Expression:
    def __init__(self, predictor):
        self.segments = []
        self.groups = []
        self.predictor = predictor
        self.preprocessor = Preprocessor()

    def feed_traces(self, traces):
        overlap_pairs = self.preprocessor.find_overlap_pairs(traces)
        tracegroups = self.preprocessor.create_tracegroups(traces, overlap_pairs)
        
        for i, group in enumerate(tracegroups):
            segment_traces = [traces[j] for j in list(group)]
            id = str(i)

            predicted_truth = self.predictor.predict(segment_traces)


            segment = Segment(id, predicted_truth, segment_traces)
            self.segments.append(segment)

        self.groups = self.recursive_search_for_context(self.segments, 10000, 0, 10000, 0)


    def recursive_search_for_context(self, objects, max_x, min_x, max_y, min_y):
        
        groups = []

        # Find all roots and sort them on width
        roots = [obj for obj in objects if obj.truth == 'sqrt']
        roots = self.sort_objects_by_width(roots)

        # Find context in roots
        for root in roots:
            if root in objects:
                objects.remove(root)

            # Find core
            core = self.find_objects_in_area(root.boundingbox.max_x, root.boundingbox.x_in_max_y, root.boundingbox.max_y, root.boundingbox.min_y, objects)

            if len(core) > 0:
                # Remove core objects from objects and roots
                for core_obj in core:
                    if core_obj in roots:
                        roots.remove(core_obj)

                    if core_obj in objects:
                        objects.remove(core_obj)

                # Send core objects to recursive search for context
                core = self.recursive_search_for_context(core, root.boundingbox.max_x, root.boundingbox.x_in_max_y, root.boundingbox.max_y, root.boundingbox.min_y)
                
                # Create Root object
                root_obj = Root(root.id, core, root.traces)

                # Add to groups
                groups.append(root_obj)
                
            else:
                print('Empty root')
                
                root_obj = Root(root.id, [], root.traces)
                groups.append(root_obj)
                

        # Find all minus signs
        minus_signs = [obj for obj in objects if obj.truth == '-']
        minus_signs = self.sort_objects_by_width(roots)

        print(minus_signs)

        # Find fractions and context in numerator/denominator
        '''
        for minus_sign in minus_signs:

            print('Found minus sign, checking for fraction')
            # Check if minus sign can be a fraction, check if there are objects over and under
            obj_is_frac, numerator, denominator = self.check_if_fraction(minus_sign, objects, max_y, min_y)

            if obj_is_frac:
                print('Found fraction')
                objects.remove(minus_sign)

                # Remove fraction objects found from objects

                
                # Find context in numerator
                

                # Find context in denominator


                # Create Fraction object

                
                # Add to groups
                
        '''

        # Find all integrals


        # Find all sums


        # Find equalsigns
        
        
        # Add single segments outside any groups
        groups = groups + objects

        # Sort groups by mid_x value
        groups = self.sort_objects_by_x_value(groups)

        # Find exponents


        return groups




    def find_objects_in_area(self, max_x, min_x, max_y, min_y, objects):
        # Find segments and groups in specified area
        # Searches for middle values (mid_x, mid_y)
        # Format:
        # 
        # min_x, min_y ---------------
        # |                          |
        # |                          |
        # ----------------max_x, max_y

        # To return:
        objects_found = []

        # Find segments in area
        for obj in objects:
            if min_x < obj.boundingbox.mid_x < max_x and min_y < obj.boundingbox.mid_y < max_y:
                objects_found.append(obj)

        return objects_found


    def check_if_fraction(self, minus_sign, objects, max_y, min_y):

        max_x = minus_sign.boundingbox.max_x
        min_x = minus_sign.boundingbox.min_x

        numerator = self.find_objects_in_area(max_x, min_x, minus_sign.boundingbox.mid_y - 1, min_y, objects)
        denominator = self.find_objects_in_area(max_x, min_x, max_y, minus_sign.boundingbox.mid_y + 1, objects)

        if len(numerator) > 0 and len(denominator) > 0:
            return False, numerator, denominator
        else:
            return True, numerator, denominator


    def horizontal_search(self, start_object, max_x_diff):
        # Find objects in a horizontal sequence

        object_sequence = [start_object]
        
        objects_found = self.find_objects_in_area(start_object.boundingbox.mid_x + 100, start_object.boundingbox.mid_x, start_object.boundingbox.mid_y + 50, start_object.boundingbox.mid_y - 50)

        #while len(objects_found) > 0:
            # sort found objects by x
            # add first to sequence
            # search again with first object
            

        return object_sequence
    

    def sort_objects_by_width(self, objects):
        return sorted(objects, key=lambda x: x.boundingbox.width, reverse=True)


    def sort_objects_by_x_value(self, objects):
        return sorted(objects, key=lambda x: x.boundingbox.mid_x, reverse=False)


    def to_latex(self):
        latex = ''
        for group in self.groups:
            latex += group.to_latex()

        return latex


class Preprocessor:
    def __init__(self):
        pass


    def find_single_trace_distances(self, trace):
        trace_cycle = cycle(trace)
        next(trace_cycle)

        distances = []

        for point in trace[:-1]:
            next_point = next(trace_cycle)
            dist = math.hypot(next_point[0] - point[0], next_point[1] - point[1])

            distances.append(dist)
        return distances

    
    def add_points_to_trace(self, trace, goal):
        
        while len(trace) < goal:
            to_add = goal - len(trace)

            if to_add > len(trace):
                to_add = len(trace) - 1

            distances = self.find_single_trace_distances(trace)
            distances_index = [[j, i] for i, j in enumerate(distances)]
            sorted_distances_index = np.asarray(sorted(distances_index, reverse=True))
            
            for i in sorted_distances_index[0:to_add, 1]:
                index = int(i)

                new_x = (trace[index][0] + trace[index + 1][0]) / 2
                new_y = (trace[index][1] + trace[index + 1][1]) / 2

                trace = np.insert(trace, index+1, np.array((new_x, new_y)), axis=0)
        
        return trace

    
    def find_overlap_pairs(self, traces):
        overlap_pairs = set()

        traces_with_added_points = []

        for i, trace in enumerate(traces):
            new_trace = self.add_points_to_trace(trace, len(trace)*2)
            traces_with_added_points.append(new_trace)

        for i, trace in enumerate(traces[:-1]):
            for j, trace2 in enumerate(traces[i+1:]):
                for coord1 in trace:
                    for coord2 in trace2:
                        if math.hypot(coord2[0] - coord1[0], coord2[1] - coord1[1]) < 10:
                            overlap_pairs.add((i, i+j+1))
        
        return overlap_pairs

    
    def create_tracegroups(self, traces, trace_pairs):
        tracegroups = []
        
        for i, trace in enumerate(traces):

            flag = False
            for j, group in enumerate(tracegroups):

                common = []
                for p in trace_pairs:
                    if i in p:
                        common = common + list(p)
                common = list(set(common))

                if len(set(common).intersection(group)) > 0:
                     tracegroups[j] = list(set(common + group))
                     flag = True

            if not flag:
                new_group = [i]
                for pair in trace_pairs:
                    if i in pair:
                        new_group = new_group + list(pair)
                
                new_group = list(set(new_group))
                tracegroups.append(new_group)
            
        sorted_tracegroups = sorted(tracegroups, key=lambda m:next(iter(m)))
        return sorted_tracegroups


class Predictor:

    CLASS_INDICES = {']': 17, 'z': 38, 'int': 23, 'sqrt': 32, '3': 7, '\\infty': 22, 'neq': 27, '6': 10, '0': 4, '[': 16, '7': 11, '4': 8, '(': 0, 'x': 36, '\\alpha': 18, '\\lambda': 24, '\\beta': 19, '\\rightarrow': 30, '8': 12, ')': 1, '=': 14, 'y': 37, '\\phi': 28, '\\times': 35, '1': 5, '<': 25, '\\Delta': 15, '\\gamma': 20, '9': 13, '\\pi': 29, '2': 6, '\\sum': 33, '\\theta': 34, '\\mu': 26, '-': 3, '>': 21, '+': 2, '\\sigma': 31, '5': 9}

    def __init__(self, model_path):
        self.model = keras.models.load_model(model_path)


    def predict(self, segment_traces):
        input_image = self.create_image(segment_traces)
        truth_proba = self.model.predict_proba(input_image)

        proba_index = np.argmax(truth_proba[0])
        for key, value in Predictor.CLASS_INDICES.items():
            if value == proba_index:
                return key


    def scale_linear_bycolumn(self, rawpoints, high=24, low=0, ma=0, mi=0):
        mins = mi
        maxs = ma

        rng = maxs - mins

        output = high - (((high - low) * (maxs - rawpoints)) / rng)

        return output

    def create_image(self, traces):
        resolution = 26
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

        return np.asarray([np.asarray(image).reshape((26, 26, 1))])

def main():
    s1 = Segment(0, '1')
    s2 = Segment(1, '+')
    s3 = Segment(2, '2')

    sg1 = Segmentgroup(3, 3.4, [s1, s2, s3])

    f1 = Fraction(4, 2.4, [sg1], [s3])
    f2 = Fraction(4, 2.4, [f1], [s3])
    
    print(f2.to_latex())


    
    pass

if __name__ == '__main__':
    main()