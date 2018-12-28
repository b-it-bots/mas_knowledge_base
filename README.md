# ``mas_knowledge_base``

# Table of Contents
1. [Summary](#summary)
2. [Package organisation](#package-organisation)
3. [Dependencies](#dependencies)
4. [Short API description](#short-api-description)
    1. [mas_knowledge_utils](#mas_knowledge_utils)
        1. [ontology_query_interface](#ontology_query_interface)
    2. [mas_knowledge_base](#mas_knowledge_base)
        1. [knowledge_base_interface](#knowledge_base_interface)
        2. [domestic_kb_interface](#domestic_kb_interface)

## Summary

`mas_knowledge_base` is a collection of packages for equipping robots with capabilities for using knowledge in their operation. We particularly consider two types of knowledge robots may have:
1. *Ontological knowledge* about concepts in the world and the connections between those; this knowledge is mostly static and rarely changes
2. *Online knowledge* about the world that gets updated as a robot operates in the environment. Online knowledge can further be divided into two groups (this division of knowledge goes in line with how [ROSPlan](http://kcl-planning.github.io/ROSPlan/documentation/) defines its knowledge base):
    1. Symbolic knowledge about the world (e.g. a bottle may be on a table or a spoon might be in a kitchen drawer)
    2. Complete information about objects in the world (e.g. the pose and the point cloud of an object)

The above division of knowledge is used as a building block for the two Python packages that are defined in this repository:
* `mas_knowledge_utils`: A ROS-independent package that implements functionalities for ontology interaction. The packages assumes that ontologies are defined using [OWL](https://www.w3.org/OWL/) and provides an interface for interacting with those.
* `mas_knowledge_base`: A ROS-dependent package that implements functionalities for interacting with online knowledge. The dependency on ROS arises because the package makes use of MongoDB store and the ROSPlan knowledge base.

In addition to these packages, the repository includes one ontology - a so-called apartment ontology - that defines classes of objects encountered in a common domestic environment.

## Package organisation

The package has the following structure:
```
mas_knowledge_base
|    package.xml
|    CMakeLists.txt
|    setup.py
|    README.md
|    LICENSE
|____common
|    |____mas_knowledge_utils
|    |    |    __init__.py
|    |    |    ontology_query_interface.py
|    |    |____domestic_ontology_interface.py
|    |
|    |____ontology
|    |    |____apartment.owl
|    |
|____ros
     |____src
          |____mas_knowledge_base
               |    __init__.py
               |    knowledge_base_interface.py
               |____domestic_kb_interface.py


```

## Dependencies

* ``rdflib`` (for the ontology query interface)
* ``termcolor``
* ``mongodb_store`` (for the knowledge base interface)
* ``rosplan_knowledge_msgs`` (for the knowledge base interface)

## Short API description

### mas_knowledge_utils

#### ontology_query_interface

The ontology query interface exposes the following methods:
* `is_instance_of`: Returns True if an object is an instance of a given class and False otherwise
* `get_instances_of`: Returns a list of all instances belonging to a given class
* `get_subclasses_of`: Returns a list of all subclasses of a given class
* `get_parent_classes_of`: Returns a list of all ancestor classes of a given class
* `get_subjects_of`: Returns a list of all subjects related to a given object through a given property `(subject property object)`
* `get_objects_of`: Returns a list of all objects related to a given subject through a given property `(subject property object)`

#### domestic_ontology_interface

The domestic ontology interface exposes methods useful for domestic applications.

The following methods are exposed by the domestic interface:
* `get_default_storing_location`: Returns a string representing the location where a specific item or an item of a given category is stored by default

### mas_knowledge_base

#### knowledge_base_interface

The knowledge base interface exposes methods for interacting both with the ROSPlan symbolic knowledge base and with MongoDB store. The following methods are exposed for interacting with the symbolic knowledge base:
* `get_all_attributes`: Returns a list of all instances of a given predicate
* `update_kb`: Inserts facts into and removes facts from the knowledge base
* `insert_facts`: Inserts a list of facts into the knowledge base
* `remove_facts`: Removes a list of facts from the knowledge base

The following methods are exposed for interacting with MongoDB store (most of which are just wrappers around the built-in MongoDB store methods):
* `insert_objects`: Inserts a list of named objects into the knowledge base
* `update_objects`: Updates a list of named objects in the knowledge base
* `remove_objects`: Removes a list of named objects from the knowledge base
* `get_objects`: Retrieves a list of named objects of a given type from the knowledge base
* `insert_obj_instance`: Inserts a named object instance into the knowledge base
* `update_obj_instance`: Updates a named object instance in the knowledge base
* `remove_obj_instance`: Removes a named object instance with a given type from the knowledge base
* `get_obj_instance`: Retrieves a named object of a given type from the knowledge base

#### domestic_kb_interface

The domestic knowledge base interface exposes methods common for domestic applications.

The following methods are exposed for interacting with the symbolic knowledge base:
* `get_surface_object_names`: Returns a list of names of objects that are on a given surface
* `get_robot_location`: Returns a string representing the location of a robot
* `get_surface_name`: Returns the name of a surface that contains a given name prefix
* `is_surface_empty`: Checks whether the surface with a given name is empty of objects
* `get_object_location`: Given an object name, returns the name of its location and a predicate indicating the relation of the object and the location ("in" or "on"). Both return values are None if the given object is unknown
* `get_surface_object_map`: Returns a dictionary in which the keys are surfaces whose names contain a given prefix and the values are lists of surface objects
* `get_obj_category_map`: Returns a dictionary in which the keys are object names and the values are the objects' categories
* `get_object_category`: Returns the category of an object with a given name; returns an empty string if the object is unknown
* `get_surface_category_counts`: Returns a nested dictionary in which the keys are surface names and the values are object counts for each object category on the surface

The following methods are exposed for interacting with MongoDB store:
* `get_surface_object_pose_map`: Returns a nested dictionary in which each key is a surface name and each value is a dictionary of the names of the objects on the surface along with their poses as stored in the knowledge base
