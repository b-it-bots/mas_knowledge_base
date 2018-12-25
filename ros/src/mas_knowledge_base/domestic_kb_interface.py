'''Module defining interfaces for knowledge base interactions
specific to domestic applications.
'''

from mas_knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class DomesticKBInterface(KnowledgeBaseInterface):
    '''Defines an interface for performing knowledge base operations common
    for a domestic application.

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self):
        super(DomesticKBInterface, self).__init__()

    ############################################################################
    #--------------------------- Symbolic knowledge ---------------------------#
    ############################################################################
    def get_surface_object_names(self, surface_name):
        '''Returns a list of names of all objects on the given surface.

        Keyword arguments:
        @param surface_name -- string representing the name of a surface

        '''
        surface_objects = list()
        on_instances = self.get_all_attributes('on')
        for item in on_instances:
            object_on_desired_surface = False
            object_name = ''
            if not item.is_negative:
                for param in item.values:
                    if param.key == 'plane' and param.value == surface_name:
                        object_on_desired_surface = True
                    elif param.key == 'obj':
                        object_name = param.value
            if object_on_desired_surface:
                surface_objects.append(object_name)
        return surface_objects

    def get_robot_location(self, robot_name):
        '''Returns a string representing the location of the robot
        as specified by the robot_at attribute; an empty string
        is returned if the location is not specified.

        Keyword arguments:
        @param robot_name -- string representing the name of a robot

        '''
        robot_at_instances = self.get_all_attributes('robot_at')
        robot_location = ''
        for item in robot_at_instances:
            if not item.is_negative:
                for param in item.values:
                    if param.key == 'bot' and param.value != robot_name:
                        break
                    if param.key == 'wp':
                        robot_location = param.value
                        break
                break
        return robot_location

    def get_surface_name(self, surface_prefix):
        '''Returns the name of a surface whose name contains the given prefix.
        If there are multiple surfaces that contain the prefix, returns the
        name of the first instance.

        Keyword arguments:
        @param surface_prefix -- string included in a surface name

        '''
        explored_instances = self.get_all_attributes('explored')
        for item in explored_instances:
            for param in item.values:
                if param.key == 'plane' and param.value.find(surface_prefix) != -1:
                    return param.value
        return ''

    def is_surface_empty(self, surface_name):
        '''Returns True if there are no objects on the given surfaces; returns False otherwise.

        Keyword arguments:
        @param surface_name -- string representing the name of a surface

        '''
        no_objects_on_surface = True
        on_instances = self.get_all_attributes('on')
        for item in on_instances:
            object_on_desired_surface = False
            if not item.is_negative:
                for param in item.values:
                    if param.key == 'plane' and param.value.find(surface_name) != -1:
                        object_on_desired_surface = True
            if object_on_desired_surface:
                no_objects_on_surface = False
                break
        return no_objects_on_surface

    def get_surface_object_map(self, surface_prefix):
        '''Returns a dictionary of objects on the surfaces whose names contain the
        given prefix, such that each key is a surface name
        and each value is a list of objects on the surface.

        Keyword arguments:
        @param surface_prefix -- name prefix of the surfaces that should be considered

        '''
        surface_objects = {}
        on_instances = self.get_all_attributes('on')
        for item in on_instances:
            object_on_desired_surface = False
            object_name = ''
            surface_name = ''
            if not item.is_negative:
                for param in item.values:
                    if param.key == 'plane' and param.value.find(surface_prefix) != -1:
                        object_on_desired_surface = True
                        surface_name = param.value
                        if surface_name not in surface_objects:
                            surface_objects[surface_name] = []
                    elif param.key == 'obj':
                        object_name = param.value
            if object_on_desired_surface:
                surface_objects[surface_name].append(object_name)
        return surface_objects

    def get_obj_category_map(self):
        '''Returns a dictionary of objects and object categories in which
        each key represents an object and the value is its category.
        '''
        category_instances = self.get_all_attributes('object_category')
        obj_category_dict = {}
        for item in category_instances:
            obj_name = ''
            obj_category = ''
            for param in item.values:
                if param.key == 'obj':
                    obj_name = param.value
                elif param.key == 'cat':
                    obj_category = param.value
            obj_category_dict[obj_name] = obj_category
        return obj_category_dict

    def get_object_category(self, obj_name):
        '''Returns the category of the given object if the object is known.
        Returns an empty string if the object is unknown.

        @param obj_name -- string representing the name of an object

        '''
        obj_category_map = self.get_obj_category_map()
        if obj_name in obj_category_map:
            return obj_category_map[obj_name]
        return ''

    def get_surface_category_counts(self, surface_prefix='', obj_category_map=None):
        '''Returns a dictionary of surfaces and object category counts in which
        each key represents a surface in the environment and the value
        is a dictionary of object counts for each category.

        Keyword arguments:
        @param surface_prefix -- name prefix of the surfaces that should be considered
                                 (default '')
        @param obj_category_map -- a dictionary of objects and their categories
                                   (default None, in which case a call to
                                   self.get_obj_category_map is made)

        '''
        if not obj_category_map:
            obj_category_map = self.get_obj_category_map()
        surface_category_counts = {}

        # we take all explored surfaces and populate 'surface_category_counts'
        # with an empty dictionary for each surface; each such dictionary
        # will store the object category count for the respective surface
        explored_instances = self.get_all_attributes('explored')
        for item in explored_instances:
            surface_name = ''
            for param in item.values:
                if param.key == 'plane':
                    surface_name = param.value
                    # we don't want to place items on the table, so we
                    # don't consider the table as a placing surface
                    if surface_name not in surface_category_counts and \
                       surface_name.find(surface_prefix) != -1:
                        surface_category_counts[surface_name] = {}

        # we populate surface_category_counts with
        # the object category counts for each surface
        on_instances = self.get_all_attributes('on')
        for item in on_instances:
            obj_name = ''
            obj_surface = ''
            for param in item.values:
                if param.key == 'obj':
                    obj_name = param.value
                elif param.key == 'plane':
                    obj_surface = param.value

            if obj_surface.find(surface_prefix) != -1:
                obj_category = obj_category_map[obj_name]
                if obj_category not in surface_category_counts[obj_surface]:
                    surface_category_counts[obj_surface][obj_category] = 1
                else:
                    surface_category_counts[obj_surface][obj_category] += 1
        return surface_category_counts

    ############################################################################
    #------------------------------ Data storage ------------------------------#
    ############################################################################
    def get_surface_object_pose_map(self, surface_object_map, obj_type):
        '''Returns a dictionary of surfaces and object poses, namely each key
        is a surface from the given dictionary and each value is a dictionary of
        object names and poses.

        Keyword arguments:
        @param surface_object_map -- a dictionary of surfaces and objects on them
        @param obj_type -- type of the objects to be retrieved
                           (the value of the objects' "_type" field)

        '''
        object_poses = {}
        for surface, objects in surface_object_map.items():
            object_poses[surface] = {}
            for obj_name in objects:
                obj = self.get_obj_instance(obj_name, obj_type)
                if obj:
                    object_poses[surface][obj_name] = obj.pose
        return object_poses
