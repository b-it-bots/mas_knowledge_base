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

    def get_classes(self):
        '''Returns a list with the names of all classes in the ontology.
        '''
        return [self.__extract_class_name(triple[0]) for triple in self.knowledge_graph[:]
                if triple[1] == URIRefConstants.RDF_TYPE and \
                   triple[2] == URIRefConstants.OWL_CLASS]

    def get_object_properties(self):
        '''Returns a list with the names of all object properties in the ontology.
        '''
        return [self.__extract_class_name(triple[0]) for triple in self.knowledge_graph[:]
                if triple[1] == URIRefConstants.RDF_TYPE and \
                   triple[2] == URIRefConstants.OWL_OBJECT_PROPERTY]

    def is_instance_of(self, obj_name, class_name):
        '''Checks whether 'obj_name' is an instance of 'class_name'.

        Keyword arguments:
        obj_name -- string representing the name of an object
        class_name -- string representing the name of a class

        '''
        return obj_name in self.get_instances_of(class_name)

    def get_instances_of(self, class_name):
        '''Returns a list of names of all instances belonging to 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        rdf_class = self.__format_class_name(class_name)
        query_result = self.knowledge_graph.query('SELECT ?instance ' +
                                                  'WHERE {?instance rdf:type ' + rdf_class + '}')
        instances = [self.__extract_obj_name(x[0]) for x in query_result]
        return instances

    def get_subclasses_of(self, class_name):
        '''Returns a list of all subclasses of 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        rdf_class_uri = rdflib.URIRef(self.__format_class_name(class_name))
        query_result = self.knowledge_graph.transitive_subjects(rdflib.RDFS.subClassOf,
                                                                rdf_class_uri)
        subclasses = [self.__extract_class_name(subclass)
                      for subclass in [str(x) for x in query_result]]
        return subclasses

    def get_parent_classes_of(self, class_name):
        '''Returns a list of all parent classes of 'class_name'.

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        rdf_class_uri = rdflib.URIRef(self.__format_class_name(class_name))
        query_result = self.knowledge_graph.transitive_objects(rdf_class_uri,
                                                               rdflib.RDFS.subClassOf)
        parent_classes = [self.__extract_class_name(parent_class)
                          for parent_class in [str(x) for x in query_result]]
        return parent_classes

    def get_subjects_of(self, prop, obj):
        '''Returns a list of subject of the relation involving the given object and property
        (i.e. given a property "subject prop object", returns a list of all subject
        involved with the object). Returns an empty list if the object
        doesn't have the given property or does not exist in the ontology.

        Keyword arguments:
        @param prop -- string representing the name of a property
        @param object -- string representing an entity in the ontology

        '''
        object_url = self.__get_entity_url(obj)
        rdf_property = self.__format_class_name(prop)
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
        subject_url = self.__get_entity_url(subject)
        rdf_property = self.__format_class_name(prop)
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
        rdf_property = self.__format_class_name(prop)
        query_result = self.knowledge_graph.query('SELECT ?subj ?obj ' +
                                                  'WHERE {?subj ' + rdf_property + ' ?obj}')
        subj_obj_pairs = [(self.__extract_obj_name(x[0]),
                           self.__extract_obj_name(x[1]))
                          for x in query_result]
        return subj_obj_pairs

    def get_property_domain_range(self, prop):
        '''Returns a pair in which the first element is the domain of the
        given property and the second element is its range.

        Keyword arguments:
        @param prop: str -- name of a property

        '''
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

    def __format_class_name(self, class_name):
        '''Returns a string of the format "self.class_prefix:class_name".

        Keyword arguments:
        @param class_name -- string representing the name of a class

        '''
        return '{0}:{1}'.format(self.class_prefix, class_name)

    def __get_entity_url(self, entity):
        '''Returns a string of the format "self.ontology_url/entity"

        Keyword arguments:
        @param entity -- string representing the name of an entity in the ontology

        '''
        return '{0}/{1}'.format(self.ontology_url, entity)

    def __extract_class_name(self, rdf_class):
        '''Extracts the name of a class given a string
        of the format "self.class_prefix:class_name".

        Keyword arguments:
        @param rdf_class -- string of the form "prefix:class"

        '''
        return rdf_class[rdf_class.find(':')+1:]

    def __extract_obj_name(self, obj_url):
        '''Extracts the name of an object from the given full URL,
        where the name is the last element of the URL.

        Keyword arguments:
        @param obj_url -- object URL in string format

        '''
        return obj_url[obj_url.rfind('/')+1:]
