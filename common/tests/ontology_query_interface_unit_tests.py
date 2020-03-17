import unittest
import os
from mas_knowledge_utils.ontology_query_interface import OntologyQueryInterface

class ontology_query_interface_test(unittest.TestCase):
    '''Implements unit tests for the OntologyQueryInterface APIs
    using the sample.owl ontology

    @author Sushant Chavan
    @contact sushant.chavan@smail.inf.h-brs.de

    '''

    def setUp(self):
        # Get directory paths
        script_dir = os.path.abspath(os.path.dirname(__file__))
        ontology_dir = os.path.join(os.path.dirname(script_dir), "ontology")

        # Get the filepath and namespace for the ontology
        self.ontology_file_path = "file://" + os.path.join(ontology_dir, "sample.owl")
        self.ontology_ns = "apartment"

        # Create an instance of the ontology interface
        self.ont_if = OntologyQueryInterface(ontology_file=self.ontology_file_path,
                                             class_prefix=self.ontology_ns)

    def test_get_classes(self):
        validation_data = ['Drinkware', 'Furniture', 'Location', 'Mug', 
                           'Object', 'Room', 'Table', 'WorkTable']
        acquired_data = sorted(self.ont_if.get_classes())
        self.assertEqual(acquired_data, validation_data)

    def test_get_object_properties(self):
        validation_data = ['defaultStoringLocation', 'heightOf', 'locatedAt']
        acquired_data = sorted(self.ont_if.get_object_properties())
        self.assertEqual(acquired_data, validation_data)

    def test_get_instances(self):
        validation_data = ['CoffeeMug', 'Desk', 'HomeOffice']
        acquired_data = sorted(self.ont_if.get_instances())
        self.assertEqual(acquired_data, validation_data)

    def test_is_instance_of(self):
        self.assertTrue(self.ont_if.is_instance_of("CoffeeMug", "Mug"))
        self.assertFalse(self.ont_if.is_instance_of("Desk", "Mug"))

    def test_get_class_hierarchy(self):
        validation_data = {'Drinkware': ['Mug'], 'Mug': [], 'WorkTable': [],
                           'Table': ['WorkTable'], 'Location': ['Room'],
                           'Room': [], 'Furniture': ['Table', 'WorkTable'],
                           'Object': ['Drinkware', 'Furniture', 'Mug', 'Table', 'WorkTable']
                          }
        acquired_data = self.ont_if.get_class_hierarchy()
        self.assertEqual(sorted(list(acquired_data.keys())),
                         sorted(list(validation_data.keys())))

        for class_name in acquired_data.keys():
            self.assertEqual(sorted(acquired_data[class_name]), 
                             validation_data[class_name])

    def test_get_instances_of(self):
        validation_data = ['HomeOffice']
        acquired_data = sorted(self.ont_if.get_instances_of("Room"))
        self.assertEqual(acquired_data, validation_data)

    def test_get_subclasses_of(self):
        validation_data = ['Furniture', 'Table', 'WorkTable']
        acquired_data = self.ont_if.get_subclasses_of("Furniture")
        self.assertEqual(acquired_data, validation_data)

    def test_get_parent_classes_of(self):
        validation_data = ['Table', 'Furniture', 'Object']
        acquired_data = self.ont_if.get_parent_classes_of("Table")
        self.assertEqual(acquired_data, validation_data)

    def test_get_objects_of(self):
        validation_data = ['HomeOffice']
        acquired_data = sorted(self.ont_if.get_objects_of("locatedAt", "Desk"))
        self.assertEqual(acquired_data, validation_data)

    def test_get_subjects_of(self):
        validation_data = ['Desk']
        acquired_data = sorted(self.ont_if.get_subjects_of("locatedAt", "HomeOffice"))
        self.assertEqual(acquired_data, validation_data)

    def test_get_all_subjects_and_objects(self):
        validation_data = [('Desk', 'HomeOffice')]
        acquired_data = sorted(self.ont_if.get_all_subjects_and_objects("locatedAt"))
        self.assertEqual(acquired_data, validation_data)

    def test_get_property_domain_range(self):
        validation_data = ('Object', 'Room')
        acquired_data = self.ont_if.get_property_domain_range("locatedAt")
        self.assertEqual(acquired_data, validation_data)

    def test_is_class(self):
        self.assertTrue(self.ont_if.is_class("Table"))
        self.assertFalse(self.ont_if.is_class("Desk"))
        self.assertFalse(self.ont_if.is_class("locatedAt"))

    def test_is_property(self):
        self.assertTrue(self.ont_if.is_property("locatedAt"))
        self.assertFalse(self.ont_if.is_property("Table"))
        self.assertFalse(self.ont_if.is_property("Desk"))

    def test_is_instance(self):
        self.assertTrue(self.ont_if.is_instance("Desk"))
        self.assertFalse(self.ont_if.is_instance("Table"))
        self.assertFalse(self.ont_if.is_instance("locatedAt"))

    def test_insert_class_assertion(self):
        # Ensure that the instances don't already exist
        self.assertFalse(self.ont_if.is_instance("Kitchen"))
        self.assertFalse(self.ont_if.is_instance("DiningTable"))
        self.assertFalse(self.ont_if.is_instance("Cup"))

        # Assert new instances
        self.ont_if.insert_class_assertion("Room", "Kitchen")
        self.ont_if.insert_class_assertion("Table", "DiningTable")
        self.ont_if.insert_class_assertion("Drinkware", "Cup")

        # Check if the new instances are added to the ontology
        self.assertTrue(self.ont_if.is_instance("Kitchen"))
        self.assertTrue(self.ont_if.is_instance("DiningTable"))
        self.assertTrue(self.ont_if.is_instance("Cup"))

        # Check if the new instances are setup from the right classes
        self.assertTrue(self.ont_if.is_instance_of("Kitchen", "Room"))
        self.assertTrue(self.ont_if.is_instance_of("DiningTable", "Table"))
        self.assertTrue(self.ont_if.is_instance_of("Cup", "Drinkware"))

    def test_insert_property_assertion(self):
        # Insert class assertions
        self.ont_if.insert_class_assertion("Room", "Kitchen")
        self.ont_if.insert_class_assertion("Table", "DiningTable")
        self.ont_if.insert_class_assertion("Drinkware", "Cup")

        # Ensure that the property assertions do not exist in the ontology
        self.assertEqual(self.ont_if.get_objects_of("defaultStoringLocation", "Cup"), [])
        self.assertEqual(self.ont_if.get_objects_of("locatedAt", "DiningTable"), [])
        self.assertEqual(self.ont_if.get_objects_of("heightOf", "DiningTable"), [])

        # Setup property assertions
        self.ont_if.insert_property_assertion("defaultStoringLocation", ("Cup", "DiningTable"))
        self.ont_if.insert_property_assertion("locatedAt", ("DiningTable", "Kitchen"))
        self.ont_if.insert_property_assertion("heightOf", ("DiningTable", 1.0))

        # Validate the newly asserted properties
        self.assertEqual(self.ont_if.get_objects_of("defaultStoringLocation", "Cup"), ["DiningTable"])
        self.assertEqual(self.ont_if.get_objects_of("locatedAt", "DiningTable"), ["Kitchen"])
        self.assertEqual(self.ont_if.get_objects_of("heightOf", "DiningTable"), ['1.0'])

    def test_remove_class_assertion(self):
        # Ensure that the instances already exist
        self.assertTrue(self.ont_if.is_instance("HomeOffice"))
        self.assertTrue(self.ont_if.is_instance("Desk"))
        self.assertTrue(self.ont_if.is_instance("CoffeeMug"))

        # Remove existing class assertions
        self.ont_if.remove_class_assertion("Room", "HomeOffice")
        self.ont_if.remove_class_assertion("WorkTable", "Desk")
        self.ont_if.remove_class_assertion("Mug", "CoffeeMug")

        # Check if the instances have been removed from the ontology
        self.assertFalse(self.ont_if.is_instance("HomeOffice"))
        self.assertFalse(self.ont_if.is_instance("Desk"))
        self.assertFalse(self.ont_if.is_instance("CoffeeMug"))

    def test_remove_property_assertion(self):
        # Ensure that the property assertions already exist in the ontology
        self.assertEqual(self.ont_if.get_objects_of("defaultStoringLocation", "CoffeeMug"), ["Desk"])
        self.assertEqual(self.ont_if.get_objects_of("locatedAt", "Desk"), ["HomeOffice"])
        self.assertEqual(self.ont_if.get_objects_of("heightOf", "Desk"), ['0.7'])

        # Remove property assertions
        self.ont_if.remove_property_assertion("defaultStoringLocation", ("CoffeeMug", "Desk"))
        self.ont_if.remove_property_assertion("locatedAt", ("Desk", "HomeOffice"))
        self.ont_if.remove_property_assertion("heightOf", ("Desk", '0.7'))

        # Ensure that the property assertions do not exist in the ontology
        self.assertEqual(self.ont_if.get_objects_of("defaultStoringLocation", "CoffeeMug"), [])
        self.assertEqual(self.ont_if.get_objects_of("locatedAt", "Desk"), [])
        self.assertEqual(self.ont_if.get_objects_of("heightOf", "Desk"), [])

class ontology_query_interface_test_no_class_prefix(ontology_query_interface_test):
    '''Implements unit tests for the OntologyQueryInterface APIs
    using an ontology that has no namespace (or class_prefix)

    @author Sushant Chavan
    @contact sushant.chavan@smail.inf.h-brs.de

    '''

    def setUp(self):
        # Get directory paths
        script_dir = os.path.abspath(os.path.dirname(__file__))
        ontology_dir = os.path.join(os.path.dirname(script_dir), "ontology")

        # Get the filepath for the ontology
        self.ontology_file_path = "file://" + os.path.join(ontology_dir, "sample_no_namespace.owl")
        # This ontology does not have a namespace, hence None
        self.ontology_ns = None

        # Create an instance of the ontology interface
        self.ont_if = OntologyQueryInterface(ontology_file=self.ontology_file_path,
                                             class_prefix=self.ontology_ns)

if __name__ == '__main__':
    unittest.main()
