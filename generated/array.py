import logging
from operator import index
import math
import xml.etree.ElementTree as ET

from generated.context import ContextReference


class Array(list):
    """Main class responsible for creating, reading and storing (nested) lists of the custom data types, functioning
    mostly like an array.
    """

    context = ContextReference()

    def __new__(cls, context, arg=0, template=None, shape=(), dtype=None, set_default=True):
        if cls.is_ragged_shape(shape):
            # the passed shape is 2D with an iterable in the 2nd dimension, so it's a ragged array
            return RaggedArray(shape, dtype, context, arg, template, set_default)
        if callable(getattr(dtype, 'create_array', None)):
            # there is a more efficient method of creating this array on the class (may not return Array instance)
            return dtype.create_array(shape, None, context, arg, template)
        else:
            return super(cls, cls).__new__(cls)

    def __init__(self, context, arg=0, template=None, shape=(), dtype=None, set_default=True):
        """Create a new array of the specified shape and type.
        :param context: The context object to use for this array (necessary for version and other global conditions).
        :type context: Any object which supports accessing for global conditions.
        :param arg: 'arg' parameter to use for instancing objects in this array.
        :param template: 'template' parameter to use for instancing objects in this array.
        :param shape: Shape of the resulting array. Zero-dimensional arrays are not supported.
        :type shape: Union[int, Tuple[int, ...]]
        :param dtype: The class to use for instancing objects in this array. If it supports create_array, that will
        be used instead.
        :type dtype: type
        :param set_default: Whether to create the elements of this array on init. If false, it is assumed that these
        elements will be created by another process immediately after init.
        :type set_default: bool, optional
        """
        super().__init__(self)
        self._shape = None
        self.shape = shape
        self.dtype = dtype
        self._context = context
        self.arg = arg
        self.template = template
        self.io_start = 0
        self.io_size = 0
        if set_default:
            self.set_defaults()

    def set_defaults(self):
        self[:] = self.fill(lambda: self.dtype(self.context, self.arg, self.template))

    def read(self, stream):
        self.io_start = stream.tell()
        self[:] = self.fill(lambda: self.dtype.from_stream(stream, self.context, self.arg, self.template))
        self.io_size = stream.tell() - self.io_start

    def write(self, stream):
        self.io_start = stream.tell()
        self.perform_nested_func(self, lambda x: self.dtype.to_stream(stream, x), self.ndim)
        self.io_size = stream.tell() - self.io_start

    def fill(self, function_to_generate):
        # fill every entry of this array using the function_to_generate
        if len(self.shape) > 1:
            # a multi-dimensional array must be filled with subarrays to allow .shape access on them
            array_list = [Array(self.context, self.arg, self.template, self.shape[1:], self.dtype, set_default=False) for _ in range(self.shape[0])]
            self[:] = [array.fill(function_to_generate) for array in array_list]
        else:
            self[:] = [function_to_generate() for _ in range(self.shape[0])]
        return self

    @classmethod
    def assign_from_function(cls, instance, function_to_generate, ndim):
        # assign every element of the array with a value generated via function_to_generate
        # assumes that every element of the array already exists
        if ndim > 1:
            [cls.assign_from_function(subarray, function_to_generate, ndim - 1) for subarray in instance]
        else:
            for i in range(len(instance)):
                instance[i] = function_to_generate()

    @staticmethod
    def is_ragged_shape(shape):
        return hasattr(shape, "__getitem__") and len(shape) == 2 and hasattr(shape[1], "__iter__")

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None, shape=(), dtype=None):
        if cls.is_ragged_shape(shape):
            return RaggedArray.from_stream(stream, context, arg, template, shape, dtype)
        # basic types have read_array method defined on their class
        elif callable(getattr(dtype, 'read_array', None)):
            return dtype.read_array(stream, shape, context, arg, template)
        else:
            new_array = cls(context, arg, template, shape, dtype, set_default=False)
            new_array.read(stream)
            return new_array

    @classmethod
    def to_stream(cls, stream, instance, dtype=None):
        if instance is not None:
            try:
                if cls.is_ragged_shape(getattr(instance, "shape", len(instance))):
                    RaggedArray.to_stream(stream, instance, dtype)
                elif callable(getattr(dtype, 'write_array', None)):
                    dtype.write_array(stream, instance)
                else:
                    # this must be an instance of cls that has the write function on itself
                    instance.write(stream)
            except:
                logging.exception(f"Array.to_stream failed for {instance} {dtype}")

    @classmethod
    def from_value(cls, shape, dtype, value):
        if cls.is_ragged_shape(shape):
            return RaggedArray.from_value(shape, dtype, value)
        elif callable(getattr(dtype, 'create_array', None)):
            return dtype.create_array(shape, default=value)
        else:
            new_array = cls(shape, dtype, None, set_default=False)
            new_array.fill(lambda: dtype.from_value(value))
            return new_array

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape_input):
        # conversion to int happens using the 'index' operator
        try:
            # try to convert iterable to a tuple of ints
            shape = tuple(index(i) for i in shape_input)
        except TypeError:
            # if this can't be converted to a tuple, try instead to convert an integer-like to (int, )
            shape = (index(shape_input),)
        # if self._shape is None:
        self._shape = shape
        # else:
        #     if self._shape != shape:
        #         raise ValueError(f'tried to assign non-compatible shape {shape} to array {self._shape}')

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def size(self):
        return math.prod(self.shape)

    @classmethod
    def perform_nested_func(cls, nested_iterable, efunc, ndim):
        # perform a function efunc(element) on every element in a nested iterable and return the result
        if ndim > 1:
            return [cls.perform_nested_func(sublist, efunc, ndim - 1) for sublist in nested_iterable]
        else:
            return [efunc(element) for element in nested_iterable]

    def store_params(self, context, arg, template, shape, dtype):
        self._context = context
        self.arg = arg
        self.template = template
        self.shape = shape
        self.dtype = dtype

    @classmethod
    def _get_filtered_attribute_list(cls, instance, dtype, include_abstract=True):
        if cls.is_ragged_shape(getattr(instance, "shape", ())):
            return RaggedArray._get_filtered_attribute_list(instance, dtype, include_abstract)
        elif callable(getattr(dtype, "_get_filtered_attribute_list_array", None)):
            return dtype._get_filtered_attribute_list_array(instance, include_abstract)
        else:
            arg = getattr(instance, "arg", 0)
            template = getattr(instance, "template", None)
            if len(instance.shape) > 1:
                for i in range(instance.shape[0]):
                    yield (i, cls, (arg, template, instance.shape[1:], dtype), (False, None))
            else:
                for i in range(instance.shape[0]):
                    yield (i, dtype, (arg, template), (False, None))

    @classmethod
    def validate_instance(cls, instance, context, arguments):
        if cls.is_ragged_shape(arguments[2]):
            return RaggedArray.validate_instance(instance, context, arguments)
        elif callable(getattr(arguments[3], "validate_array", None)):
            return arguments[3].validate_array(instance, context, arguments[:3])
        try:
	        assert instance.context == context, f"context {instance.context} doesn't match {context} on {cls}"
	        assert instance.arg == arguments[0], f"argument {instance.argument} doesn't match {arguments[0]} on {cls}"
	        assert instance.template == arguments[1], f"template {instance.template} doesn't match {arguments[1]} on {cls}"
	        assert instance.shape == arguments[2], f"shape {instance.shape} doesn't match {arguments[2]} on {cls}"
	        assert instance.dtype == arguments[3], f"dtype {instance.dtype} doesn't match {arguments[3]} on {cls}"
        except AssertionError:
            logging.error(f"validation failed on {cls}[{arguments[3]}]")
            raise
        for f_name, f_type, f_arguments, _ in cls._get_filtered_attribute_list(instance, arguments[3]):
            try:
                f_type.validate_instance(cls.get_field(instance, f_name), context, f_arguments)
            except AssertionError:
                logging.error(f"validation failed on field {f_name} on type {cls}[{arguments[3]}]")
                raise

    @staticmethod
    def get_field(instance, key):
        return instance[key]

    @staticmethod
    def set_field(instance, key, value):
        instance[key] = value

    @classmethod
    def get_size(cls, context, instance, arguments):
        size = 0
        for field_name, field_type, arguments, _ in cls._get_filtered_attribute_list(instance, *arguments[3:4], include_abstract=False):
            size += field_type.get_size(context, cls.get_field(instance, field_name), arguments)
        return size

    @staticmethod
    def fmt_member(member, indent=0):
        lines = str(member).split("\n")
        lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
        return "\n".join(lines_new)

    @property
    def class_name(self):
        """Returns the lowercase name of the class, eg. 'variant'"""
        return _class_to_name(self.dtype).lower()

    @classmethod
    def from_xml(cls, instance, elem, prop, arguments):
        arg, template, shape, dtype = arguments
        sub = elem.find(f'.//{prop}')
        if sub is None:
            logging.warning(f"Missing sub-element '{prop}' on XML element '{elem.tag}'")
            return
        if callable(getattr(dtype, "_from_xml_array", None)):
            return dtype._from_xml_array(None, sub)
        instance = Array(instance.context, arg, template, shape, dtype, set_default=False)
        cls._from_xml(instance, sub)
        return instance

    @classmethod
    def _from_xml(cls, instance, elem):
        # init each member from corresponding sub-elem
        instance[:] = [instance.dtype._from_xml(instance.dtype(instance._context, 0, instance.template), sub) for sub in elem]
        return instance

    @classmethod
    def to_xml(cls, elem, prop, instance, arguments, debug):
        arg, template, shape, dtype = arguments
        sub = ET.SubElement(elem, prop)
        if callable(getattr(dtype, "_to_xml_array", None)):
            dtype._to_xml_array(instance, sub, debug)
            return
        cls._to_xml(instance, sub, debug)

    @classmethod
    def _to_xml(cls, instance, elem, debug):
        dtype = instance.dtype
        dtype_name = dtype.__name__.lower()
        for member in instance:
            dtype.to_xml(elem, dtype_name, member, (), debug)


class RaggedArray(Array):
    """Class responsible for creating, reading and storing (nested) lists of the custom data types, functioning
    mostly like a 2D ragged array. Not referenced directly in code generation.
    """

    context = ContextReference()

    def __new__(cls, context, arg=0, template=None, shape=(), dtype=None, set_default=True):
        if callable(getattr(dtype, 'create_ragged_array', None)):
            # there is a more efficient method of creating this array on the class (may not return RaggedArray instance)
            return dtype.create_ragged_array(shape, None, context, arg, template)
        else:
            return list.__new__(cls)

    def fill(self, function_to_generate):
        # fill every entry of this array using the function_to_generate
        # a multi-dimensional array must be filled with subarrays to allow .shape access on them
        array_list = [Array(self.context, self.arg, self.template, (self.shape[1][i], *self.shape[2:]), self.dtype, set_default=False) for i in range(self.shape[0])]
        if callable(getattr(self.dtype, "create_array", None)):
            # the dtype has not returned an Array type, and may therefore not have a .fill function
            type(self).assign_from_function(array_list, function_to_generate, self.ndim)
        else:
            self[:] = [array.fill(function_to_generate) for array in array_list]
        return self

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape_input):
        # conversion to int happens using the 'index' operator
        shape = (index(shape_input[0]), shape_input[1], *(index(i) for i in shape_input[2:]))
        self._shape = shape

    @property
    def size(self):
        return self.shape[0] * sum(self.shape[1]) * math.prod(self.shape[2:])

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None, shape=(), dtype=None):
        # basic types have read_array method defined on their class
        if callable(getattr(dtype, 'read_ragged_array', None)):
            return dtype.read_ragged_array(stream, shape, context, arg, template)
        else:
            new_array = cls(shape, dtype, context, arg, template, set_default=False)
            new_array.read(stream)
            return new_array

    @classmethod
    def to_stream(cls, stream, instance, dtype=None):
        if instance is not None:
            if callable(getattr(dtype, 'write_ragged_array', None)):
                dtype.write_ragged_array(stream, instance)
            else:
                instance.write(stream)

    @classmethod
    def from_value(cls, shape, dtype, value):
        if callable(getattr(dtype, 'create_ragged_array', None)):
            return dtype.create_ragged_array(shape, default=value)
        else:
            new_array = cls(shape, dtype, None, set_default=False)
            new_array.fill(lambda: dtype.from_value(value))
            return new_array

    @classmethod
    def _get_filtered_attribute_list(cls, instance, dtype, include_abstract=True):
        if callable(getattr(dtype, "_get_filtered_attribute_list_ragged_array", None)):
            return dtype._get_filtered_attribute_list_ragged_array(instance, include_abstract)
        else:
            arg = getattr(instance, "arg", 0)
            template = getattr(instance, "template", None)
            for i in range(instance.shape[0]):
                yield (i, cls, (arg, template, instance.shape[1][i], dtype), (False, None))

    @classmethod
    def validate_instance(cls, instance, context, arguments):
        if callable(getattr(arguments[3], "validate_ragged_array", None)):
            return arguments[3].validate_ragged_array(instance, context, arguments[:3])
        try:
	        assert instance.context == context, f"context {instance.context} doesn't match {context} on {cls}"
	        assert instance.arg == arguments[0], f"argument {instance.argument} doesn't match {arguments[0]} on {cls}"
	        assert instance.template == arguments[1], f"template {instance.template} doesn't match {arguments[1]} on {cls}"
	        assert instance.shape == arguments[2], f"shape {instance.shape} doesn't match {arguments[2]} on {cls}"
	        assert instance.dtype == arguments[3], f"dtype {instance.dtype} doesn't match {arguments[3]} on {cls}"
        except AssertionError:
            logging.error(f"validation failed on {cls}[{arguments[3]}]")
            raise
        for f_name, f_type, f_arguments, _ in cls._get_filtered_attribute_list(instance, arguments[3]):
            try:
                f_type.validate_instance(cls.get_field(instance, f_name), context, f_arguments)
            except AssertionError:
                logging.error(f"validation failed on field {f_name} on type {cls}[{arguments[3]}]")
                raise


def _class_to_name(cls):
    cls_str = str(cls)
    if "." in cls_str:
        # <class 'generated.formats.dinosaurmaterialvariants.compounds.Variant.Variant'>
        _, a = cls_str.rsplit(".", 1)
        b, _ = a.rsplit("'", 1)
        return b
    # eg for enums
    return cls.__name__
