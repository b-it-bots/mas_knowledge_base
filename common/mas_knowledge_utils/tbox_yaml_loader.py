import yaml
import argparse
import os
from mas_knowledge_utils.ontology_query_interface import OntologyQueryInterface

class TBoxYAMLLoader:
    '''Updates an ontology with new class and property definitions 
    that are specified in a yaml file.

    Constructor arguments:
    @param ontology_file -- full URL of an ontology file (of the form file://<absolute-path>)
    @param ontology_class_prefix -- class prefix of the items in the given ontology
    @param definitions_file -- absolute-path to the yaml file containing definitions
    @param verbose -- boolean to enable debug console logging, which is disabled by default.

    @author Sushant Chavan
    @contact sushant.chavan@smail.inf.h-brs.de

    '''
    def __init__(self, ontology_file, ontology_class_prefix, definitions_file, verbose=False):
        self.ontology_if = OntologyQueryInterface(ontology_file=ontology_file,
                                    class_prefix=ontology_class_prefix, verbose=verbose)
        self.class_definitions = None
        self.property_definitions = None
        self.prefix = ontology_class_prefix
        self.verbose = verbose

        self.__load_definitions(definitions_file)

    def update_ontology(self, export_path):
        '''Inserts the class and property definitions and updates/exports the ontology.

        Keyword arguments:
        export_path -- string representing the filepath (of the form file://<absolute-path>)
                       if the ontology has to be exported to a new file. 
                       If it is 'None', the loaded ontology will be updated with the definitions

        '''
        self.process_class_definitions()
        self.process_property_definitions()
        self.export_ontology(export_path)

    def process_class_definitions(self):
        '''Inserts the class definitions into the loaded ontology.
        '''
        if self.class_definitions is None:
            return

        while len(self.class_definitions):
            for class_name in self.__get_independent_classes():
                parents = self.class_definitions[class_name]
                self.ontology_if.insert_class_definition(class_name, parents)
                # Remove processed class_name entries from the pending list
                del self.class_definitions[class_name]
                self.__verbose("Added new class: {0} with parents: {1}".format(
                    class_name, parents))

    def process_property_definitions(self):
        '''Inserts the property definitions into the loaded ontology.
        '''
        if self.property_definitions is None:
            return

        for property_name in self.property_definitions.keys():
            domain_ns, domain = self.property_definitions[property_name]['domain']
            range_ns, range = self.property_definitions[property_name]['range']
            prop_type = self.property_definitions[property_name]['type']
            self.ontology_if.insert_property_definition(property_name, domain,
                                                        range, prop_type,
                                                        domain_ns, range_ns)
            self.__verbose("Added new property: {0}, with domain={1}:{2}, range={3}:{4} "
                "and type={5}".format(property_name, domain_ns if domain_ns else self.prefix,
                domain, range_ns if range_ns else self.prefix, range, prop_type))

    def export_ontology(self, export_path):
        '''Updates/exports the ontology.

        Keyword arguments:
        export_path -- string representing the filepath (of the form file://<absolute-path>)
                       if the ontology has to be exported to a new file. 
                       If it is 'None', the loaded ontology will be updated with the definitions

        '''
        if export_path is None:
            # Overwrite the existing ontology file with the updated ontology
            self.__verbose("No export filepath specified. Updating the loaded ontology.")
            self.ontology_if.update()
        else:
            # Save the updated ontology at the given file location
            self.__verbose("Exporting the ontology to {0}".format(export_path))
            self.ontology_if.export(export_path)

    def __get_independent_classes(self):
        '''Returns a list of class_names in the loaded class_definitions whose 
        parent classes have already been defined in the ontology, i.e. they are 
        not dependent on any classes in the self.class_definitions which are yet
        to be inserted in the ontology.

        For example, consider the following class definitions:
        class_definitions:
            Person: []
            Male: [Person]
            Female: [Person]
        Here, it is necessary that the Person class is inserted into the ontology 
        before the Male and Female classes to avoid triggering an assert that 
        verifies if the parent classes exist in the ontology. However, since the
        class_definitions are loaded as a dictionary, the order of the classes 
        cannot be maintained. The first call to this method therefore returns only
        the Person class. Once it is inserted into the ontology, the next call to
        this method will return the Male and Female classes.
        '''
        independent_classes = []
        for name, parents in self.class_definitions.items():
            is_independent = True
            for parent in parents:
                if not self.ontology_if.is_class(parent):
                    is_independent = False
                    break
            if is_independent:
                independent_classes.append(name)
        if not independent_classes and self.class_definitions:
            raise Exception('Could not find indpendent class names from the loaded class descriptions!')
        return independent_classes

    def __load_definitions(self, definitions_file):
        '''Loads the class and property definitions as two separate
        dictionaries from the yaml file

        Keyword arguments:
        definitions_file -- absolute-path to the yaml file containing definitions

        '''
        definitions = None
        with open(definitions_file, 'r') as f:
            definitions = yaml.load(f, Loader=yaml.FullLoader)

        if definitions is None:
            raise Exception("Could not load the definition file!")
        else:
            self.class_definitions = definitions['class_definitions']
            self.property_definitions = definitions['property_definitions']

            # Convert any loaded 'None' strings to None data-type
            for property_name in self.property_definitions.keys():
                domain = []
                for d in self.property_definitions[property_name]['domain']:
                    domain.append(self.__maybe_none(d))
                self.property_definitions[property_name]['domain'] = domain

                range = []
                for r in self.property_definitions[property_name]['range']:
                    range.append(self.__maybe_none(r))
                self.property_definitions[property_name]['range'] = range

                self.property_definitions[property_name]['type'] = \
                    self.__maybe_none(self.property_definitions[property_name]['type'])
    
    def __maybe_none(self, value):
        '''Returns None datatype if the value is equal to 'None',
        otherwise returns the value without modifications

        Keyword arguments:
        value -- string representing the entity to be checked

        '''
        return None if value =='None' else value

    def __verbose(self, content):
        '''Console debug logger to print the content along with the
        '[TBoxYAMLLoader]' tag only if the self.verbose flag is set

        Keyword arguments:
        @param content -- string representing the content to be printed

        '''
        if self.verbose:
            print("[TBoxYAMLLoader] {0}".format(content))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('definitions', type=str, 
                        help="Name of the yaml file containing the definitions \
                              (eg.: apartment_definitions)")
    parser.add_argument('-o', '--ontology', type=str, action='store', 
                        help="Filename of the ontology (default: apartment_go_2019)",
                        default='apartment_go_2019')
    parser.add_argument('-c', '--class-prefix', type=str, action='store', 
                        help="class prefix (or namespace) of the items in the \
                              given ontology (default: apartment)",
                        default='apartment')
    parser.add_argument('-e', '--export-file', type=str, action='store', 
                        help="Filename for exporting the updated ontology \
                              (eg.: apartment_go_2019_updated). If not \
                               specified, the loaded ontology will be updated.",
                        default=None)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Enable debug console logs")

    args = parser.parse_args()

    script_dir = os.path.abspath(os.path.dirname(__file__))
    ontology_dir = os.path.join(os.path.dirname(script_dir), "ontology")
    definitions_dir = os.path.join(os.path.dirname(script_dir), "definitions")

    ontology_file_path = "file://" + os.path.join(ontology_dir, args.ontology + ".owl")
    definitions_file_path = os.path.join(definitions_dir, args.definitions + ".yaml")

    export_file_path = None
    if args.export_file is not None:
        export_file_path = "file://" + os.path.join(ontology_dir, args.export_file + ".owl")

    loader = TBoxYAMLLoader(ontology_file_path, args.class_prefix, 
                            definitions_file_path, verbose=args.verbose)
    loader.update_ontology(export_file_path)
