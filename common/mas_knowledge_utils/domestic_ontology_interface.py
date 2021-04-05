'''Module defining interfaces for interacting with an OWL ontology
that are specific to domestic applications.
'''

from termcolor import colored
from mas_knowledge_utils.ontology_query_interface import OntologyQueryInterface

class DomesticOntologyInterface(OntologyQueryInterface):
    '''Defines an interface for interacting with an ontology
    specific to domestic applications.

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self, ontology_file, base_url=None, entity_delimiter='/', class_prefix=''):
        super(DomesticOntologyInterface, self).__init__(ontology_file=ontology_file,
                                                        base_url=base_url,
                                                        entity_delimiter=entity_delimiter,
                                                        class_prefix=class_prefix)

    def get_default_storing_location(self, obj_name=None, obj_category=None):
        '''Returns a string representing the default storing location of an
        object or an object category. If "obj_name" is not None, returns the
        default storing location for that particular object; if "obj_name"
        is None and "obj_category" is not, returns the default storing location
        for objects that category.

        Keyword arguments:
        @param obj_name -- string representing the name of an object (default None)
        @param obj_category -- string representing the category of an object (default None)

        '''
        location = None
        if obj_name:
            location_list = self.get_objects_of('defaultStoringLocation', obj_name)
            if location_list:
                location = location_list[0]
        elif obj_category:
            # TODO: define class restrictions for category-wide default storing locations
            pass
        else:
            error_msg = '[get_default_storing_location] obj_name and obj_category cannot both be None'
            raise AssertionError(error_msg)
        return location

    def get_obj_location(self, obj_name):
        '''Returns the location of the given object or None
        if there location is unknown.

        Keyword arguments:
        @param obj_name -- string representing the name of an object

        '''
        obj_location = None
        if obj_name:
            location_list = self.get_objects_of('locatedAt', obj_name)
            if location_list:
                try:
                    obj_location = location_list[0]
                except:
                    print(colored('[get_obj_location] Location of {0} unknown'.format(obj_name), 'yellow'))
        else:
            error_msg = '[get_obj_height] obj_name cannot be None'
            raise AssertionError(error_msg)
        return obj_location

    def get_objects_next_to(self, obj_name):
        '''Returns all objects that are next to the given object.

        Keyword arguments:
        @param obj_name -- string representing the name of an object

        '''
        next_to_obj_list = []
        if obj_name:
            next_to_objects = set(self.get_objects_of('nextTo', obj_name))
            next_to_subjects = set(self.get_subjects_of('nextTo', obj_name))
            next_to_obj_list = list(next_to_subjects.union(next_to_objects))
        else:
            error_msg = '[get_objects_next_to] obj_name cannot be None'
            raise AssertionError(error_msg)
        return next_to_obj_list

    def get_obj_height(self, obj_name):
        '''Returns a floating point number representing the height of the given object.

        Keyword arguments:
        @param obj_name -- string representing the name of an object

        '''
        height = 0.
        if obj_name:
            height_list = self.get_objects_of('heightOf', obj_name)
            if height_list:
                try:
                    height = float(height_list[0])
                except:
                    print(colored('[get_obj_height] Height is not a floating-point number', 'red'))
                    raise
        else:
            error_msg = '[get_obj_height] obj_name cannot be None'
            raise AssertionError(error_msg)
        return height
