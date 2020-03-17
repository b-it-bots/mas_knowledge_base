'''Module defining interfaces for interacting with an OWL ontology.
'''

import rdflib

class URIRefConstants(object):
    RDF_TYPE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    OWL_CLASS = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')
    OWL_OBJECT_PROPERTY = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#ObjectProperty')
    OWL_INVERSE_OF = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#inverseOf')
    PROPERTY_DOMAIN = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#domain')
    PROPERTY_RANGE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#range')

class OntologyQueryInterface(object):
    '''Defines an interface for interacting with an OWL knowledge base.

    Constructor arguments:
    @param ontology_file -- full URL of an ontology file (of the form file://<absolute-path>)
    @param class_prefix -- class prefix of the items in the given ontology

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''

    def __init__(self, ontology_file, class_prefix):
        self.knowledge_graph = rdflib.Graph()
        self.knowledge_graph.load(ontology_file)
        self.class_prefix = class_prefix
        self.ontology_url = ontology_file[0:ontology_file.rfind('/')]
        self.ontology_file = ontology_file

        self.__class_names = None
        self.__instance_names = None
        self.__property_names = None

    def get_classes(self):
        '''Returns a list with the names of all classes in the ontology.
        '''
        if self.__class_names is not None:
            return self.__class_names

        self.__class_names = [self.__extract_class_name(triple[0]) for triple in self.knowledge_graph[:]
                              if triple[1] == URIRefConstants.RDF_TYPE and \
                              triple[2] == URIRefConstants.OWL_CLASS]
        return self.__class_names

    def get_object_properties(self):
        '''Returns a list with the names of all object properties in the ontology.
        '''
        if self.__property_names is not None:
            return self.__property_names

        self.__property_names = [self.__extract_class_name(triple[0]) for triple in self.knowledge_graph[:]
                                 if triple[1] == URIRefConstants.RDF_TYPE and \
                                 triple[2] == URIRefConstants.OWL_OBJECT_PROPERTY]
        return self.__property_names

    def get_instances(self):
        '''Returns a list with the names of all instances in the ontology.
        '''
        if self.__instance_names is not None:
            return self.__instance_names

        self.__instance_names = []
        class_list = self.get_classes()
        for c in class_list:
            self.__instance_names.extend(self.get_instances_of(c))
        return list(set(self.__instance_names))

    def is_class(self, class_name):
        '''Checks whether 'class_name' is defined as a class in the ontology.

        Keyword arguments:
        class_name -- string representing the name of the class

        '''
        return class_name in self.get_classes()

    def is_instance(self, instance_name):
        '''Checks whether 'instance_name' is defined as a class instance in the ontology.

        Keyword arguments:
        instance_name -- string representing the name of the class instance

        '''
        return instance_name in self.get_instances()

    def is_property(self, property_name):
        '''Checks whether 'property_name' is defined as a property in the ontology.

        Keyword arguments:
        property_name -- string representing the name of the property

        '''
        return property_name in self.get_object_properties()

    def is_instance_of(self, obj_name, class_name):
        '''Checks whether 'obj_name' is an instance of 'class_name'.

        Keyword arguments:
        obj_name -- string representing the name of an object
        class_name -- string representing the name of a class

        '''
        if not self.is_instance(obj_name):
            raise ValueError('"{0}" does not exist as an instance in the ontology!'.format(obj_name))
        elif not self.is_class(class_name):
            raise ValueError('"{0}" does not exist as a class in the ontology!'.format(class_name))
        else:
            return obj_name in self.get_instances_of(class_name)
        return False

    def get_class_hierarchy(self):
        '''Returns a dictionary in which each key is a class and the value
        is a list of subclasses of that class. The dictionary thus represents
        the hierarchy of classes in the ontology.
        '''
        classes = self.get_classes()
        class_hierarchy = {}
        for c in classes:
            subclasses = self.get_subclasses_of(c)

            # we remove the class from the list since a class is also a subclass of itself
            subclasses.remove(c)

            class_hierarchy[c] = subclasses
        return class_hierarchy

    def get_instances_of(self, class_name):
        '''Returns a list of names of all instances belonging to 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        if self.is_class(class_name):
            rdf_class = self.__format_class_name(class_name, as_sparql_url=True)
            query_result = self.knowledge_graph.query('SELECT ?instance ' +
                                                      'WHERE {?instance rdf:type ' + rdf_class + '}')
            instances = [self.__extract_obj_name(x[0]) for x in query_result]
            return instances
        else:
            raise ValueError('"{0}" does not exist as a class in the ontology!'.format(class_name))

    def get_subclasses_of(self, class_name):
        '''Returns a list of all subclasses of 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        if self.is_class(class_name):
            rdf_class_uri = rdflib.URIRef(self.__format_class_name(class_name))
            query_result = self.knowledge_graph.transitive_subjects(rdflib.RDFS.subClassOf,
                                                                    rdf_class_uri)
            subclasses = [self.__extract_class_name(subclass)
                          for subclass in [str(x) for x in query_result]]
            return subclasses
        else:
            raise ValueError('"{0}" does not exist as a class in the ontology!'.format(class_name))

    def get_parent_classes_of(self, class_name):
        '''Returns a list of all parent classes of 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        if self.is_class(class_name):
            rdf_class_uri = rdflib.URIRef(self.__format_class_name(class_name))
            query_result = self.knowledge_graph.transitive_objects(rdf_class_uri,
                                                                   rdflib.RDFS.subClassOf)
            parent_classes = [self.__extract_class_name(parent_class)
                              for parent_class in [str(x) for x in query_result]]
            return parent_classes
        else:
            raise ValueError('"{0}" does not exist as a class in the ontology!'.format(class_name))

    def get_subjects_of(self, prop, obj):
        '''Returns a list of subject of the relation involving the given object and property
        (i.e. given a property "subject prop object", returns a list of all subject
        involved with the object). Returns an empty list if the object
        doesn't have the given property or does not exist in the ontology.

        Keyword arguments:
        @param prop -- string representing the name of a property
        @param object -- string representing an entity in the ontology

        '''
        if not self.is_property(prop):
            raise ValueError('"{0}" does not exist as a property in the ontology!'.format(prop))
        elif not self.is_instance(obj):
            raise ValueError('"{0}" does not exist as an instance in the ontology!'.format(obj))
        else:
            object_url = self.__get_entity_url(obj)
            rdf_property = self.__format_class_name(prop, as_sparql_url=True)
            query_result = self.knowledge_graph.query('SELECT ?subj ' +
                                                      'WHERE {?subj ' + rdf_property +
                                                      ' <' + object_url +  '>}')
            subject_list = [self.__extract_obj_name(x[0]) for x in query_result]
            return subject_list

    def get_objects_of(self, prop, subject):
        '''Returns a list of objects of the relation involving the given subject and property
        (i.e. given a property "subject prop object", returns a list of all objects
        involved with the subject). Returns an empty list if the subject
        doesn't have the given property or does not exist in the ontology.

        Keyword arguments:
        @param prop -- string representing the name of a property
        @param subject -- string representing an entity in the ontology

        '''
        if not self.is_property(prop):
            raise ValueError('"{0}" does not exist as a property in the ontology!'.format(prop))
        elif not self.is_instance(subject):
            raise ValueError('"{0}" does not exist as an instance in the ontology!'.format(subject))
        else:
            subject_url = self.__get_entity_url(subject)
            rdf_property = self.__format_class_name(prop, as_sparql_url=True)
            query_result = self.knowledge_graph.query('SELECT ?obj ' +
                                                      'WHERE {<' + subject_url + '> ' +
                                                      rdf_property + ' ?obj}')
            object_list = [self.__extract_obj_name(x[0]) for x in query_result]
            return object_list

    def get_all_subjects_and_objects(self, prop):
        '''Returns a list of pairs in which the first element is the subject
        and the second element is the object of each (subject prop object)
        triple in the ontology.

        Keyword arguments:
        @param prop: str -- name of a property

        '''
        if self.is_property(prop):
            rdf_property = self.__format_class_name(prop, as_sparql_url=True)
            query_result = self.knowledge_graph.query('SELECT ?subj ?obj ' +
                                                      'WHERE {?subj ' + rdf_property + ' ?obj}')
            subj_obj_pairs = [(self.__extract_obj_name(x[0]),
                               self.__extract_obj_name(x[1]))
                              for x in query_result]
            return subj_obj_pairs
        else:
            raise ValueError('"{0}" does not exist as a property in the ontology!'.format(prop))

    def get_property_domain_range(self, prop):
        '''Returns a pair in which the first element is the domain of the
        given property and the second element is its range.

        Keyword arguments:
        @param prop: str -- name of a property

        '''
        if self.is_property(prop):
            prop_domain = None
            prop_range = None
            rdf_property = rdflib.URIRef(self.__format_class_name(prop))
            for triple in self.knowledge_graph[:]:
                if triple[0] == rdf_property:
                    if triple[1] == URIRefConstants.PROPERTY_DOMAIN:
                        prop_domain = self.__extract_class_name(triple[2])
                    elif triple[1] == URIRefConstants.PROPERTY_RANGE:
                        prop_range = self.__extract_class_name(triple[2])
                    elif triple[1] == URIRefConstants.OWL_INVERSE_OF:
                        inverse_prop = self.__extract_class_name(self.__extract_obj_name(triple[2]))
                        (prop_range, prop_domain) = self.get_property_domain_range(inverse_prop)
                if prop_domain and prop_range:
                    break
            return (prop_domain, prop_range)
        else:
            raise ValueError('"{0}" does not exist as a property in the ontology!'.format(prop))

    def insert_class_assertion(self, class_name, instance_name):
        ''' Adds a new instance of a class to the ontology

        Keyword arguments:
        class_name -- string representing the name of the class
        instance_name -- string representing the name of the instance

        '''
        if self.is_class(class_name):
            self.knowledge_graph.add((rdflib.URIRef(self.__get_entity_url(instance_name)),
                                      rdflib.RDF.type,
                                      self.__get_entity_uriref(class_name)))
            # Reset instance names list to ensure that the newly added
            # instance is included in the next query to the instance_list
            self.__instance_names = None
        else:
            raise ValueError('The "{0}" class does not exist in the ontology!'.format(class_name))

    def insert_property_assertion(self, property_name, instance):
        ''' Adds a new predicate between a subject and an object to the ontology

        Keyword arguments:
        property_name -- string representing the name of the predicate
        instance -- tuple(string, string) representing the subject and the object respectively

        '''
        if not self.is_instance(instance[0]):
            raise ValueError('The subject "{0}" does not exist in the ontology as an instance of a class!'.format(instance[0]))
        # Skip the type-check for the object since it is not necessary to be a class
        # For example, the heightOf property can be a float.
        # elif not self.is_instance(instance[1]):
        #     raise ValueError('The object "{0}" does not exist in the ontology as an instance of a class!'.format(instance[1]))
        elif not self.is_property(property_name):
            raise ValueError('The property "{0}" is not defined in the ontology!'.format(property_name))
        else:
            self.knowledge_graph.add((rdflib.URIRef(self.__get_entity_url(instance[0])),
                                      self.__get_entity_uriref(property_name),
                                      rdflib.URIRef(self.__get_entity_url(instance[1]))))

    def remove_class_assertion(self, class_name, instance_name):
        ''' Removes an existing instance of a class from the ontology

        Keyword arguments:
        class_name -- string representing the name of the class
        instance_name -- string representing the name of the instance

        '''
        if not self.is_class(class_name):
            raise ValueError('The "{0}" class does not exist in the ontology!'.format(class_name))
        elif not self.is_instance(instance_name):
            raise ValueError('The "{0}" instance does not exist in the ontology!'.format(instance_name))
        elif not self.is_instance_of(instance_name, class_name):
            raise ValueError('"{0}" is not an instance of {1}!'.format(instance_name, class_name))
        else:
            self.knowledge_graph.remove((rdflib.URIRef(self.__get_entity_url(instance_name)),
                                      rdflib.RDF.type,
                                      self.__get_entity_uriref(class_name)))
            # Reset instance names list to ensure that the removed instance is
            # not included in the next query to the instance_list
            self.__instance_names = None

    def remove_property_assertion(self, property_name, instance):
        ''' Removes an existing predicate between a subject and an object from the ontology

        Keyword arguments:
        property_name -- string representing the name of the predicate
        instance -- tuple(string, string) representing the subject and the object respectively

        '''
        if not self.is_instance(instance[0]):
            raise ValueError('The subject "{0}" does not exist in the ontology as an instance of a class!'.format(instance[0]))
        # Skip the type-check for the object since it is not necessary to be a class
        # For example, the heightOf property can be a float.
        # elif not self.is_instance(instance[1]):
        #     raise ValueError('The object "{0}" does not exist in the ontology as an instance of a class!'.format(instance[1]))
        elif not self.is_property(property_name):
            raise ValueError('The property "{0}" is not defined in the ontology!'.format(property_name))
        else:
            self.knowledge_graph.remove((rdflib.URIRef(self.__get_entity_url(instance[0])),
                                      self.__get_entity_uriref(property_name),
                                      rdflib.URIRef(self.__get_entity_url(instance[1]))))

    def export(self, ontology_file, format='xml'):
        '''Exports the ontology as an xml document.

        Keyword arguments:
        @param ontology_file -- full URL of the ontology file (of the form file://<absolute-path>)

        '''
        self.knowledge_graph.serialize(ontology_file, format=format)

    def update(self, format='xml'):
        '''Overwrites the loaded ontology file with the current version of the ontology.

        '''
        self.export(self.ontology_file, format=format)

    def __format_class_name(self, class_name, as_sparql_url=False):
        '''Returns a string of the format "self.class_prefix:class_name",
        or "class_name" if self.class_prefix is empty.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        if self.class_prefix:
            return '{0}:{1}'.format(self.class_prefix, class_name)
        elif as_sparql_url:
            return '<' + self.__get_entity_url(class_name) + '>'
        else:
            return self.__get_entity_url(class_name)

    def __get_entity_url(self, entity):
        '''Returns a string of the format "self.ontology_url/entity"

        Keyword arguments:
        @param entity -- string representing the name of an entity in the ontology

        '''
        return '{0}/{1}'.format(self.ontology_url, entity)

    def __get_entity_uriref(self, entity):
        '''Returns a rdflib.URIRef object for the entity.

        Keyword arguments:
        @param entity -- string representing the name of an entity in the ontology

        '''
        if self.class_prefix:
            ns = rdflib.Namespace("http://{0}#".format(self.class_prefix))
            return rdflib.URIRef(ns[entity])
        else:
            return rdflib.URIRef(self.__get_entity_url(entity))

    def __extract_class_name(self, rdf_class):
        '''Extracts the name of a class given a string
        of the format "self.class_prefix:class_name".
        Returns "rdf_class" if self.class_prefix is empty.

        Keyword arguments:
        @param rdf_class -- string of the form "prefix:class"

        '''
        if self.class_prefix:
            return rdf_class[rdf_class.find(':')+1:]
        return self.__extract_obj_name(rdf_class)

    def __extract_obj_name(self, obj_url):
        '''Extracts the name of an object from the given full URL,
        where the name is the last element of the URL.

        Keyword arguments:
        @param obj_url -- object URL in string format

        '''
        return obj_url[obj_url.rfind('/')+1:]
