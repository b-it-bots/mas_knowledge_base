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
