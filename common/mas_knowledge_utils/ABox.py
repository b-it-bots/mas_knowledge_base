import yaml
import argparse
import os
from ontology_query_interface import OntologyQueryInterface

# TODO: name of this class?
class PopulateABox:
    '''Updates an ontology with class and property assertions 
    that are specified in a yaml file.

    Constructor arguments:
    @param ontology_file -- full URL of an ontology file (of the form file://<absolute-path>)
    @param ontology_class_prefix -- class prefix of the items in the given ontology
    @param assertions_file -- absolute-path to the yaml file containing assertions

    @author Sushant Chavan
    @contact sushant.chavan@smail.inf.h-brs.de

    '''
    def __init__(self, ontology_file, ontology_class_prefix, assertions_file):
        self.ontology_if = OntologyQueryInterface(ontology_file=ontology_file,
                                    class_prefix=ontology_class_prefix)
        self.class_assertions = None
        self.property_assertions = None

        self.__load_assertions(assertions_file)

    def update_ontology(self, export_path):
        '''Inserts the class and property assertions and updates/exports the ontology.

        Keyword arguments:
        export_path -- string representing the filepath (of the form file://<absolute-path>)
                       if the ontology has to be exported to a new file. 
                       If it is 'None', the loaded ontology will be updated with the assertions

        '''
        self.process_class_assertions()
        self.process_property_assertions()
        self.export_ontology(export_path)

    def process_class_assertions(self):
        '''Inserts the class assertions into the loaded ontology.

        '''
        if self.class_assertions is None:
            return

        for class_name in self.class_assertions.keys():
            instance_names = self.class_assertions[class_name]
            for instance_name in instance_names:
                self.ontology_if.insert_class_assertion(class_name, instance_name)
                #print("Inserting class assertion: {0}, {1}".format(class_name, instance_name))

    def process_property_assertions(self):
        '''Inserts the property assertions into the loaded ontology.

        '''
        if self.property_assertions is None:
            return

        for property_name in self.property_assertions.keys():
            for subj, obj in self.property_assertions[property_name].items():
                self.ontology_if.insert_property_assertion(property_name, (subj, obj))
                #print("Inserting property assertion: {0}, {1}, {2}".format(subj, property_name, obj))

    def export_ontology(self, export_path):
        '''Updates/exports the ontology.

        Keyword arguments:
        export_path -- string representing the filepath (of the form file://<absolute-path>)
                       if the ontology has to be exported to a new file. 
                       If it is 'None', the loaded ontology will be updated with the assertions

        '''
        if export_path is None:
            # Overwrite the existing ontology file with the updated ontology
            print("No export filepath specified. Updating the loaded ontology.")
            self.ontology_if.update()
        else:
            # Save the updated ontology at the given file location
            print("Exporting the ontology to", export_path)
            self.ontology_if.export(export_path)

    def __load_assertions(self, assertions_file):
        '''Loads the class and property assertions as two separate
        dictionaries from the yaml file

        Keyword arguments:
        assertions_file -- absolute-path to the yaml file containing assertions

        '''
        assertions = None
        with open(assertions_file, 'r') as f:
            assertions = yaml.load(f, Loader=yaml.FullLoader)

        if assertions is None:
            raise Exception("Could not load the assertion file!")
        else:
            self.class_assertions = assertions['class_assertions']
            self.property_assertions = assertions['property_assertions']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('asserts', type=str, 
                        help="Name of the yaml file containing the assertions \
                              (eg.: apartment_asserts)")
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

    args = parser.parse_args()

    script_dir = os.path.abspath(os.path.dirname(__file__))
    ontology_dir = os.path.join(os.path.dirname(script_dir), "ontology")
    assertions_dir = os.path.join(os.path.dirname(script_dir), "assertions")

    ontology_file_path = "file://" + os.path.join(ontology_dir, args.ontology + ".owl")
    assertions_file_path = os.path.join(assertions_dir, args.asserts + ".yaml")

    export_file_path = None
    if args.export_file is not None:
        export_file_path = "file://" + os.path.join(ontology_dir, args.export_file + ".owl")

    aBox = PopulateABox(ontology_file_path, args.class_prefix, assertions_file_path)
    aBox.update_ontology(export_file_path)
