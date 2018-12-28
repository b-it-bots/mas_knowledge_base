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
    def __init__(self, ontology_file, class_prefix):
        super(DomesticOntologyInterface, self).__init__(ontology_file, class_prefix)

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
            error_msg = colored('[get_default_storing_location] obj_name ' +
                                'and obj_category cannot both be None', 'red')
            print(error_msg)
        return location
